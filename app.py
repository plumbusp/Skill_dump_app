import os
import sys
import sqlite3
import math
import secrets
from flask import Flask, session, abort, make_response
from flask import redirect, render_template, request, url_for
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import private_ideas, forum, users
from werkzeug.datastructures import FileStorage
from configparser import ConfigParser # for local testing only

app = Flask(__name__)
### creating all tables in databse:
db.create_app_tables()

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    con_par = ConfigParser()
    con_par.read("config.cfg")
    file = con_par["secret-key"]["secret_key"]
    print(file)
    if not file:
        print("Secret Key is not set!", flush=True)
        sys.exit(1)
    initialized = False
    app.secret_key = file
else:
    initialized = False
    app.secret_key = SECRET_KEY 


page_size = 2

#### HELPER/ GENERAL METHODS ####
def require_log_in():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    token = request.form.get("csrf_token")
    if not token:
        abort(403)
        
    if token != session["csrf_token"]:
        abort(403)
    
#####
### HOME (NAVIGATION) ####
@app.route("/", methods = ["GET"])
def show_home():
    # Log in status is handled inside the html file
    if "user_id" in session:
        total_skills = users.get_total_skills(session["user_id"])
        skill_stats = users.get_skill_stats(session["user_id"])
        user = users.get_user(session["user_id"])
        return render_template("index.html", user=user,total_skills=total_skills,skill_stats=skill_stats)
    else:
        return render_template("index.html")


def page_validity_helper(current_page, total_pages_count)-> int:
        if current_page < 1:
            return 1
        elif current_page > total_pages_count:
            return total_pages_count
        else:
            return current_page

### SIGNING IN/ LOGGING IN ####
@app.route("/sign_up_page")
def sign_up_page():
    return render_template("sign_up_page.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("Passwords don't match!", "sign_up_exception")
        return redirect("/sign_up_page")
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO log_in_info (usernames, passwords) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("User with this username already exists", "sign_up_exception")
        return redirect("/sign_up_page")

    # succesfull sign up
    #SESSION
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    session["user_id"] = db.query("SELECT id FROM log_in_info WHERE usernames = ?", [username])[0]["id"]

    return redirect("/")


@app.route("/log_in", methods=["POST"])
def log_in():
    username = request.form.get("username") # getting a name form the submitted form
    password = request.form.get("password")

    if str(username).strip() == "" or str(password).strip() == "":
        flash("Username and/or password cannot be empty!","log_in_exception")
        return redirect("/")

    result = db.query("SELECT usernames, passwords FROM log_in_info WHERE usernames=?", (username ,))
    if result == []:
        flash("No user with this username has been found. Sign up?","log_in_exception")
        return redirect("/")
    
    if not password:
        flash("Invalid password","log_in_exception")
    elif check_password_hash(result[0][1],password):
        #SESSION
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        session["user_id"] = db.query("SELECT id FROM log_in_info WHERE usernames = ?", [username])[0]["id"]
    else: 
        flash("Invalid password","log_in_exception")
    
    return redirect("/")
    
@app.route("/logout")
def log_out():
    require_log_in()
    
    session.clear()
    return redirect("/")



#### IDEAS (PRIVATE) ####
@app.route("/private_ideas")
@app.route("/private_ideas/<int:page>")
def show_private_ideas(page=1):
    require_log_in()
   
    search_keyword = request.args.get("search_keyword") or None
    if search_keyword and search_keyword.strip == "":
        search_keyword = None

    search_skill_type = request.args.get("search_skill_type") or None
    if search_skill_type and search_skill_type.strip().lower() == "all":
        search_skill_type = None

    ideas_count = private_ideas.get_private_ideas_count(search_keyword, search_skill_type)

    if ideas_count == 0:
        flash("There is no entries that satisfy given search parameters", "private_ideas_search_exception")

    page_count = math.ceil(ideas_count/page_size)
    page = page_validity_helper(page, page_count)

    ideas = private_ideas.get_private_ideas(page, page_size, search_keyword=search_keyword,search_skill_type=search_skill_type)
    user_skill_types = users.get_users_skills(session["user_id"])
    return render_template("private_ideas.html", search_keyword=search_keyword,search_skill_type=search_skill_type, page=page, page_count=page_count, ideas=ideas,user_skill_types=user_skill_types)

@app.route("/add_private_idea", methods=["POST"])
def add_idea():
    require_log_in()
    check_csrf()

    idea = request.form["idea"]
    content = request.form["content"]
    type_of_skill = request.form["type_of_skill"]
    #print(f"type_of_skill {type_of_skill}", flush=True)

    clean_idea = idea.strip()
    clean_content = content.strip()
    
    if len(clean_idea) > 100 or len(clean_idea) == 0:
        flash("The title cannot be empty or more than 100 char!", "new_idea")
        return redirect("/private_ideas")
    
    elif len(clean_content) > 1000 or len(clean_content) == 0:
        flash("The content cannot be empty or more than 1000 char!", "new_idea")
        return redirect("/private_ideas")


    private_ideas.add_private_idea(idea, content, type_of_skill)
    return redirect("/private_ideas")

@app.route("/edit/<int:idea_id>", methods=["GET", "POST"])
def edit_idea(idea_id):
    require_log_in()

    idea = private_ideas.get_idea(idea_id)
    user_skill_types = users.get_users_skills(session["user_id"])

    if request.method == "GET":
        return render_template("edit.html", for_idea=True, for_message=False, idea=idea, user_skill_types=user_skill_types)

    if request.method == "POST":
        check_csrf()
        new_content = request.form["edited_content"]
        new_title = request.form["edited_title"]
        type_of_skill= request.form["edited_type_of_skill"]
        private_ideas.update_idea(int(idea_id),new_content, new_title, type_of_skill)
        return redirect("/private_ideas")
    
    return "what is it then?? ERROR!"


@app.route("/delete/<int:idea_id>", methods=["GET","POST"])
def delete_idea(idea_id):
    require_log_in()

    idea = private_ideas.get_idea(idea_id)

    if request.method == "GET":
        return render_template("delete.html",for_idea=True, for_message=False, idea=idea)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            private_ideas.delete_idea(idea_id)
        return redirect("/private_ideas")
    
    return "what is it then?? ERROR!"

@app.route("/search_private_ideas", methods =["GET"])
def search_private_ideas():
    require_log_in()

    keyword = request.args.get("search_keyword") or None
    skill_type = request.args.get("search_skill_type") or None
    print("KEyword ", keyword)
    print("Type of skill ", skill_type)
    
    return redirect(url_for("show_private_ideas", search_keyword= keyword, search_skill_type=skill_type))


#### SKILLS ####
@app.route("/add_skill_type", methods =["POST"])
def add_skill():
    require_log_in()
    check_csrf()

    skill = request.form["new_skill"]
    if len(skill.strip()) == 0 or len(skill.strip()) > 50:
        flash("Invalid skill input! The skill can't be empty or longer than 50 char.","skills")
    passes = users.add_type_of_skill(session["user_id"], skill)
    if not passes:
        flash("The skill name is already taken!", "skills")

    return redirect("/private_ideas")


#### THREADS (PUBLIC) ####

@app.route("/threads", methods = ["GET"])
@app.route("/threads/<int:page>", methods = ["GET"])
def show_threads(page=1):
    # Log in status is handled inside the html file
    thread_count = forum.thread_count()

    page_count = math.ceil(thread_count/page_size)
    page = page_validity_helper(page, page_count)

    threads = forum.get_threads(page, page_size)
    return render_template("threads.html", threads=threads, page=page,page_count=page_count)

@app.route("/search_threads", methods =["GET"])
def search_threads():
    require_log_in()
    keyword =request.args.get("keyword")
    if not keyword:
        return redirect("/threads")
        
    matches = forum.find_matches(keyword)
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
    check_csrf()

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
    check_csrf()
    
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
        check_csrf()
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
        return render_template("delete.html", for_idea = False, for_message = True, message=message, thread_id =thread_id, message_id=message_id)

    elif request.method == "POST":
        check_csrf()
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
    check_csrf()
    
    file = request.files["image_input"]
    if not file.filename.endswith(".jpg"):
        flash("Wrong image type! (jpg images only)", "image_exception")
        return redirect("/")

    image = file.read()
    if len(image) > 100 * 1024:
        flash("Submitted image is too big!", "image_exception")
        return redirect("/")

    user_id = session["user_id"]
    users.update_image(user_id, image)
    flash("Profile picture was updated successfully!", "image_success")
    return redirect("/")
    

@app.route("/image/<int:user_id>")
def show_image(user_id):
    require_log_in()

    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response
    
