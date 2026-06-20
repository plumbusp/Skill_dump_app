import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

def get_private_ideas(invalid_title=False, invalid_content=False, user_skill_types=[]) -> str:
    sql = """SELECT i.*, COALESCE(st.names, '') skill_type_name
            FROM ideas i
            LEFT JOIN skill_types st ON i.type_of_skill = st.id
            WHERE i.user_id = ?"""
    ideas = db.query(sql, [session["user_id"]])
    return render_template("private_ideas.html", ideas=ideas, invalid_title=invalid_title, invalid_content=invalid_content,user_skill_types=user_skill_types)

def add_private_idea(idea: str, content:str, type_of_skill:str):
    db.execute("INSERT INTO ideas (title, content, user_id, type_of_skill) VALUES (?,?,?,?)",[idea, content, session["user_id"], type_of_skill])

def get_idea(idea_id)-> dict:
    return db.query("SELECT * FROM ideas WHERE id = ?", [idea_id])[0]



def update_idea(idea_id:int, content:str, title:str):
    db.execute("UPDATE ideas SET title = ?, content = ? WHERE id = ?", [title, content, idea_id])

def delete_idea(idea_id:int):
    db.execute("DELETE FROM ideas WHERE id = ?", [idea_id])

def find_matches(keyword:str)-> list:
    return db.query("SELECT * FROM ideas WHERE title LIKE ? AND user_id = ?", [f"%{keyword}%", session["user_id"]])