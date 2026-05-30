from flask import Flask, render_template, request
import sqlite3
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("typical_page_no_log_in.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    connection = create_db()
    cursor = connection.cursor()
    username = request.form.get("username") # getting a name form the submitted form
    password = request.form.get("password")
    result = cursor.execute("SELECT 1 FROM log_in_info WHERE username = ?", (username,))
    connection.commit()
    
    # checking if username exists
    list_of_tuples = result.fetchall()
    print(list_of_tuples)
    if list_of_tuples == []:
        print("Inserting ",  (username, password))
        cursor.execute("INSERT INTO log_in_info VALUES (?,?)", (username, password))
        connection.commit()
    else:
        print("Already exists")
        return render_template("sign_up_page.html", already_exists=True)

    return "!"

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


@app.route("/sign_up_page")
def sign_up_page():
    return render_template("sign_up_page.html")

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