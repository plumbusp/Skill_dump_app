import sqlite3
from flask import Flask, session, abort
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import private_ideas, forum
import os
import sys

app = Flask(__name__)
### creating all tables in databse:
db.create_app_tables()

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Secret Key is not set!", flush=True)
    sys.exit(1)
initialized = False
app.secret_key = SECRET_KEY

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
    session.clear()
    return render_template("index.html",valid_login=True)

@app.route("/")
def log_in_page():
    return render_template("index.html",valid_login=True)


#### IDEAS (PRIVATE) ####
@app.route("/private_ideas")
def show_private_ideas():
    return private_ideas.get_private_ideas()

@app.route("/add_private_idea", methods=["POST"])
def add_idea():
    idea = request.form["idea"]
    content = request.form["content"]
    if idea.strip() == "":
        return redirect("/private_ideas")

    private_ideas.add_private_idea(idea, content)
    return redirect("/private_ideas")

@app.route("/edit/<int:idea_id>", methods=["GET", "POST"])
def edit_idea(idea_id):
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
    keyword =request.args.get("keyword")
    if not keyword:
        return redirect("/private_ideas")
    
    matches = private_ideas.find_matches(keyword)
    print(matches)
    return render_template("private_ideas.html", ideas=matches)

print(__name__)


#####
### HOME (NAVIGATION) ####
@app.route("/", methods = ["GET"])
def show_home():
    return render_template("index.html")

@app.route("/threads", methods = ["GET"])
def show_threads():
    threads = forum.get_threads()
    return render_template("threads.html", threads=threads)



#### THREADS (PUBLIC) ####
@app.route("/thread/<int:thread_id>")
def show_thread(thread_id:int):
    thread = forum.get_thread(thread_id)
    messages = forum.get_messages(thread_id)
    return render_template("thread.html", messages=messages, thread=thread)

@app.route("/create_thread", methods=["POST"])
def create_thread():
    title = request.form["title_of_new_thread"]
    initial_message = request.form["initial_message"]
    forum.add_thread(title, initial_message)

    thread_id = forum.get_last_thread_id()
    return redirect(f"/thread/{thread_id}")

@app.route("/new_message", methods = ["POST"])
def add_message():
    message = request.form["new_message"]
    thread_id = request.form["thread_id"]
    forum.add_message(message, thread_id, session["user_id"])
    return redirect(f"/thread/{thread_id}")


@app.route("/edit_message/<int:thread_id>/<int:message_id>", methods=["GET", "POST"])
def edit_message(thread_id:int, message_id: int):
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
    message = forum.get_message(thread_id, message_id)

    if message["user_id"] != session["user_id"]:
        abort(403) # Forbidden access

    if request.method == "GET":
        return render_template("delete.html", for_idea = False, for_message = True, message=message, thread =thread)

    elif request.method == "POST":
        forum.delete_message(thread_id,message_id)
        return redirect(f"/thread/{thread_id}")
        
    return redirect(f"/thread/{thread_id}")




