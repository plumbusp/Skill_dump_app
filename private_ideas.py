import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

def get_private_ideas( page, page_size, page_count, user_skill_types=None) -> str:
    sql = """SELECT i.title, i.content, i.type_of_skill, i.id
            FROM ideas i
            WHERE i.user_id = ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page-1)
    ideas = db.query(sql, [session["user_id"], limit, offset])
    return render_template("private_ideas.html", page=page, page_count=page_count, ideas=ideas,user_skill_types=user_skill_types)

def ideas_count()-> int:
    sql = """SELECT COUNT(id) AS count FROM ideas WHERE user_id = ?"""
    return db.query_one(sql, [session["user_id"]])["count"]

def add_private_idea(idea: str, content:str, type_of_skill:str):
    db.execute("INSERT INTO ideas (title, content, user_id, type_of_skill) VALUES (?,?,?,?)",[idea, content, session["user_id"], type_of_skill])

def get_idea(idea_id)-> dict:
    return db.query("SELECT * FROM ideas WHERE id = ?", [idea_id])[0]


def update_idea(idea_id:int, content:str, title:str, type_of_skill:str):
    db.execute("UPDATE ideas SET title = ?, content = ?, type_of_skill = ? WHERE id = ?", [title, content, type_of_skill, idea_id])

def delete_idea(idea_id:int):
    db.execute("DELETE FROM ideas WHERE id = ?", [idea_id])

def find_matches(keyword:str)-> list:
    return db.query("SELECT * FROM ideas WHERE title LIKE ? AND user_id = ?", [f"%{keyword}%", session["user_id"]])