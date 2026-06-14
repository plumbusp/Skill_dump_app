import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

def get_private_ideas(invalid_title=False, invalid_content=False) -> str:
    ideas = db.query("SELECT * FROM ideas WHERE user_id = ?", [session["user_id"]])
    return render_template("private_ideas.html", ideas=ideas, invalid_title=invalid_title, invalid_content=invalid_content)

def add_private_idea(idea: str, content:str):
    if not session["user_id"]:
        return "NO USER ID"
    db.execute("INSERT INTO ideas (title, content, user_id) VALUES (?,?,?)",[idea, content, session["user_id"]])

def get_idea(idea_id)-> dict:
    return db.query("SELECT * FROM ideas WHERE id = ?", [idea_id])[0]



def update_idea(idea_id:int, content:str, title:str):
    db.execute("UPDATE ideas SET title = ?, content = ? WHERE id = ?", [title, content, idea_id])

def delete_idea(idea_id:int):
    db.execute("DELETE FROM ideas WHERE id = ?", [idea_id])

def find_matches(keyword:str)-> list:
    return db.query("SELECT * FROM ideas WHERE title LIKE ? AND user_id = ?", [f"%{keyword}%", session["user_id"]])