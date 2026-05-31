import sqlite3
from flask import Flask
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash
import config
import db

app = Flask(__name__)

@app.route("/sign_up_page")
def sign_up_page():
    return render_template("sign_up_page.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "Passwords don't match!"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO log_in_info (username, password) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("sign_up_page.html", already_exists= True)

    return render_template("user_home.html")

@app.route("/")
def index():
    return render_template("typical_page_no_log_in.html")

@app.route("/log_in", methods=["POST"])
def log_in():
    connection = create_db()
    cursor = connection.cursor()
    username = request.form.get("username") # getting a name form the submitted form
    password = request.form.get("password")
    print("Username ", username)
    print("Passwro ", password)

    result = cursor.execute("SELECT username, password FROM log_in_info WHERE username=?", (username ,))
    connection.commit()
    row = result.fetchall()
    print("ROW",row)

    if row == [] or password != row[0][1]:
        print("Wrong Password")
        return render_template("log_in_page.html", valid_login=False)
    else:
        return "!!"


@app.route("/log_in_page")
def log_in_page():
    return render_template("log_in_page.html",valid_login=True)


@app.route("/<int:page_id>")
def page(page_id):
    return "Tämä on sivu " + str(page_id)

def create_db()-> sqlite3.Connection:
    """Creates a database if doens't exists. Returns connection onject"""
    connection_obj = sqlite3.connect("database.sqlite")
    connection_obj.execute("""
        CREATE TABLE IF NOT EXISTS log_in_info (
            username varchar(50) PRIMARY KEY,
            password varchar(10)
        );
                                """)
    return connection_obj
    

print(__name__)