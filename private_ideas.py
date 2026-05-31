import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

def get_private_ideas() -> str:
    ideas = db.query("SELECT * FROM ideas WHERE user_id = ?", [session["user_id"]])
    return render_template("private_ideas.html", ideas=ideas)

def add_private_idea(idea: str):
    if not session["user_id"]:
        return "NO USER ID"
    db.execute("INSERT INTO ideas (title, user_id) VALUES (?,?)",[idea, session["user_id"]])