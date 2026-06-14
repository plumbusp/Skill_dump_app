import sqlite3
from flask import Flask, session, abort,make_response
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import private_ideas, forum, users
import os
import sys
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
### creating all tables in databse:
db.create_app_tables()

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Secret Key is not set!", flush=True)
    sys.exit(1)
initialized = False
app.secret_key = SECRET_KEY

#### HELPER/ GENERAL METHODS ####
def require_log_in():
    if "user_id" not in session:
        abort(403)

### SIGNING IN/ LOGGING IN ####
@app.route("/sign_up_page")
def sign_up_page():
    return render_template("sign_up_page.html", passwords_match = True)

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return render_template("sign_up_page.html", passwords_match = False)
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO log_in_info (usernames, passwords) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("sign_up_page.html", already_exists= True)

    # succesfull sign up
    #SESSION
    session["username"] = username
    session["user_id"] = db.query("SELECT id FROM log_in_info WHERE usernames = ?", [username])[0]["id"]

    return render_template("index.html")


@app.route("/log_in", methods=["POST"])
def log_in():
    username = request.form.get("username") # getting a name form the submitted form
    password = request.form.get("password")
    print("Username ", username)
    print("Password ", password)
    if str(username).strip() == "" or str(password).strip() == "":
        print("Invalid username or password")
        return render_template("index.html",valid_login=False)

    result = db.query("SELECT usernames, passwords FROM log_in_info WHERE usernames=?", (username ,))
    if result == []:
        return render_template("index.html",valid_login=False)
    elif not password:
        print(" not password")
        return render_template("index.html",valid_login=False)
       
    if check_password_hash(result[0][1],password):
        # log in
        print("right password")
        #SESSION
        session["username"] = username
        session["user_id"] = db.query("SELECT id FROM log_in_info WHERE usernames = ?", [username])[0]["id"]
        print("user id ", session["user_id"])

        return render_template("index.html")
    else: 
        print("Invalid password")
        return render_template("index.html",valid_login=False)
    
@app.route("/logout")
def log_out():
    require_log_in()
    
    session.clear()
    return render_template("index.html",valid_login=True)

@app.route("/")
def log_in_page():
    return render_template("index.html",valid_login=True)



#### IDEAS (PRIVATE) ####
@app.route("/private_ideas")
def show_private_ideas():
    require_log_in()

    user_skill_types = users.get_users_skills(session["user_id"])
    return private_ideas.get_private_ideas(user_skill_types=user_skill_types)

@app.route("/add_private_idea", methods=["POST"])
def add_idea():
    require_log_in()

    idea = request.form["idea"]
    content = request.form["content"]
    type_of_skill = request.form["type_of_skill"]
    print(f"type_of_skill {type_of_skill}", flush=True)
    if type_of_skill == "None":
        type_of_skill = ""

    clean_idea = idea.strip()
    clean_content = content.strip()
    if len(clean_idea) > 100 or len(clean_idea) == 0:
        return private_ideas.get_private_ideas(invalid_title=True)
    elif len(clean_content) > 1000 or len(clean_content) == 0:
        return private_ideas.get_private_ideas(invalid_content=True)


    private_ideas.add_private_idea(idea, content, type_of_skill)
    return redirect("/private_ideas")

@app.route("/edit/<int:idea_id>", methods=["GET", "POST"])
def edit_idea(idea_id):
    require_log_in()

    idea = private_ideas.get_idea(idea_id)

    if request.method == "GET":
        return render_template("edit.html", for_idea=True, for_message=False, idea=idea)

    if request.method == "POST":
        new_content = request.form["edited_content"]
        new_title = request.form["edited_title"]
        private_ideas.update_idea(int(idea_id),new_content, new_title)
        return redirect("/private_ideas")
    return "what is it then?? ERROR!"


@app.route("/delete/<int:idea_id>", methods=["GET","POST"])
def delete_idea(idea_id):
    require_log_in()

    idea = private_ideas.get_idea(idea_id)

    if request.method == "GET":
        return render_template("delete.html",for_idea=True, for_message=False, idea=idea)

    if request.method == "POST":
        if "continue" in request.form:
            private_ideas.delete_idea(idea_id)
        return redirect("/private_ideas")
    
    return "what is it then?? ERROR!"

@app.route("/search_private_ideas", methods =["GET"])
def search_private_ideas():
    require_log_in()

    keyword =request.args.get("keyword")
    if not keyword:
        return redirect("/private_ideas")
    
    matches = private_ideas.find_matches(keyword)
    print(matches)
    return render_template("private_ideas.html", ideas=matches)

print(__name__)


#### SKILLS ####
@app.route("/add_skill_type", methods =["POST"])
def add_skill():
    require_log_in()

    skill = request.form["new_skill"]
    if len(skill.strip()) == 0 or len(skill.strip()) > 50:
        return "Invalid skill input! The skill can't be empty or longer than 50 char."
    users.add_type_of_skill(session["user_id"], skill)
    return redirect("/private_ideas")



#####
### HOME (NAVIGATION) ####
@app.route("/", methods = ["GET"])
def show_home(user=None):
    # Log in status is handled inside the html file

    if "user_id" in session:
        print("USER IDD", flush=True)
        total_skills = users.get_total_skills(session["user_id"])
        skill_stats = users.get_skill_stats(session["user_id"])
        user = users.get_user(session["user_id"])
        return render_template("index.html", user=user,total_skills=total_skills,skill_stats=skill_stats)
    else:
        return render_template("index.html")



#### THREADS (PUBLIC) ####

@app.route("/threads", methods = ["GET"])
def show_threads():
    # Log in status is handled inside the html file
    threads = forum.get_threads()
    return render_template("threads.html", threads=threads)

@app.route("/search_threads", methods =["GET"])
def search_threads():
    require_log_in()
    keyword =request.args.get("keyword")
    if not keyword:
        return redirect("/threads")
        
    matches = forum.find_matches(keyword)
    print(matches)
    return render_template("threads.html", threads=matches)


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id:int):
    require_log_in()

    thread = forum.get_thread(thread_id)
    if not thread: # If user went to the thread that does not exist
        abort(403)
    messages = forum.get_messages(thread_id)
    return render_template("thread.html", messages=messages, thread=thread)


@app.route("/create_thread", methods=["POST"])
def create_thread():
    require_log_in()

    title = request.form["title_of_new_thread"]
    clean_title = title.strip()
    if len(clean_title) == 0 or len(clean_title) > 100:
        abort(403) 

    initial_message = request.form["initial_message"]
    clean_message = initial_message.strip()
    if len(clean_message) == 0 or len(clean_message) > 500:
        abort(403)

    forum.add_thread(title, initial_message)

    thread_id = forum.get_last_thread_id()
    return redirect(f"/thread/{thread_id}")

@app.route("/new_message", methods = ["POST"])
def add_message():
    require_log_in()
    
    try:
        message = request.form["new_message"]
        clean_message = message.strip()
        if len(clean_message) == 0 or len(clean_message) > 500:
            abort(403)

        thread_id = request.form["thread_id"]
        forum.add_message(message, thread_id, session["user_id"])
        return redirect(f"/thread/{thread_id}")
    except: # catches internal server error, if e.g. a user changed thread_id in page inspection to the unexisting one
        abort(403)


@app.route("/edit_message/<int:thread_id>/<int:message_id>", methods=["GET", "POST"])
def edit_message(thread_id:int, message_id: int):
    require_log_in()

    thread = forum.get_thread(thread_id)
    message = forum.get_message(thread_id, message_id)

    if message["user_id"] != session["user_id"]:
        abort(403) # Forbidden access

    if request.method == "GET":
        return render_template("edit.html", for_idea = False, for_message = True, message=message, thread=thread)

    elif request.method == "POST":
        new_contemt = request.form["content"]
        forum.update_message(thread_id, message_id, new_contemt)
        return redirect(f"/thread/{thread_id}")
        
    return redirect(f"/thread/{thread_id}")

@app.route("/delete_message/<int:thread_id>/<int:message_id>", methods=["GET", "POST"])
def delete_message(thread_id:int, message_id: int):
    require_log_in()

    message = forum.get_message(thread_id, message_id)

    if message["user_id"] != session["user_id"]:
        abort(403) # Forbidden access

    if request.method == "GET":
        return render_template("delete.html", for_idea = False, for_message = True, message=message, thread =thread)

    elif request.method == "POST":
        forum.delete_message(thread_id,message_id)
        return redirect(f"/thread/{thread_id}")
        
    return redirect(f"/thread/{thread_id}")


#### USER PROFILES ######
@app.route("/user/<int:user_id>")
def show_user(user_id):
    require_log_in()

    if user_id == session["user_id"]:
        return redirect("/")
    
    user = users.get_user(user_id)
    if not user:
        abort(404)
    last_messages = users.get_last_messages(user_id)
    print("last messages: ", last_messages, flush=True)
    return render_template("user.html", user=user, last_messages=last_messages)

### USER IMAGES ###
@app.route("/add_image", methods=["POST"])
def add_image():
    require_log_in()
    
    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        return "Wrong image type! (jpg images only)"

    image = file.read()
    if len(image) > 100 * 1024:
        return "The image it too big!"

    user_id = session["user_id"]
    users.update_image(user_id, image)
    user = users.get_user(user_id)
    return show_home(user=user)
    

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response
    
