import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

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
    return render_template("private_ideas.html")



print(__name__)