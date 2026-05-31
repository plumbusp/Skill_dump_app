import db
from flask import session
def get_private_ideas():
    ideas = db.query("SELECT * FROM ideas WHERE user_id = ?", [session["user_id"]])
    print(ideas)