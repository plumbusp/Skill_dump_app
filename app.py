import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import private_ideas

app = Flask(__name__)
app.secret_key = config.secret_key
initialized = False

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

    return render_template("log_in_page.html")

@app.route("/")
def index():
    print(session.get("test"))
    return render_template("typical_page_no_log_in.html")

@app.route("/log_in", methods=["POST"])
def log_in():
    username = request.form.get("username") # getting a name form the submitted form
    password = request.form.get("password")
    print("Username ", username)
    print("Password ", password)

    result = db.query("SELECT usernames, passwords FROM log_in_info WHERE usernames=?", (username ,))
    print(f"Result { result[0][0]} { result[0][1]}")
    if not password:
        print(" not password")
        return render_template("log_in_page.html",valid_login=False)
       
    if check_password_hash(result[0][1],password):
        # log in
        print("right password")
        #SESSION
        session["username"] = username
        session["user_id"] = db.query("SELECT id FROM log_in_info WHERE usernames = ?", [username])[0]["id"]
        print("user id ", session["user_id"])

        return render_template("log_in_page.html")
    else: 
        print("Invalid password")
        return render_template("log_in_page.html",valid_login=False)
@app.route("/logout")
def log_out():
    session.clear()
    return render_template("log_in_page.html",valid_login=True)

@app.route("/log_in_page")
def log_in_page():
    return render_template("log_in_page.html",valid_login=True)

@app.route("/<int:page_id>")
def page(page_id):
    return "Tämä on sivu " + str(page_id)

@app.route("/to_private_ideas")
def show_private_ideas():
    return private_ideas.get_private_ideas()

@app.route("/add_private_idea", methods=["POST"])
def add_private_idead():
    idea = request.form["idea"]
    if idea.strip() == "":
        return redirect("/to_private_ideas")

    private_ideas.add_private_idea(idea)
    return redirect("/to_private_ideas")

@app.route("/edit/<int:idea_id>", methods=["GET", "POST"])
def edit_idea(idea_id):
    idea = private_ideas.get_idea(idea_id)

    if request.method == "GET":
        return render_template("edit.html", idea=idea)

    if request.method == "POST":
        content = request.form["content"]
        private_ideas.update_idea(idea["id"], content)
        return redirect("/to_private_ideas")
    return "what is it then?? ERROR!"


@app.route("/remove/<int:idea_id>", methods=["GET","POST"])
def remove_message(idea_id):
    idea = private_ideas.get_idea(idea_id)

    if request.method == "GET":
        return render_template("remove.html", idea=idea)

    if request.method == "POST":
        if "continue" in request.form:
            private_ideas.remove_idea(idea["id"])
        return redirect("/to_private_ideas")
    
    return "what is it then?? ERROR!"

@app.route("/search_private_ideas", methods =["GET"])
def search_private_ideas():
    keyword =request.args.get("keyword")
    if not keyword:
        return redirect("/to_private_ideas")
    matches = private_ideas.find_matches(keyword)
    print(matches)
    return render_template("private_ideas.html", ideas=matches)

print(__name__)