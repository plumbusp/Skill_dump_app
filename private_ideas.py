import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

def get_private_ideas(page, page_size, search_keyword=None, search_skill_type=None) -> list:
    limit = page_size
    offset = page_size * (page-1)
    params = [session["user_id"]]
    print("search_keyword", search_keyword)
    print("search_skill_type",search_skill_type)
    if search_keyword == None and search_skill_type == None:
        sql = """SELECT i.title, i.content, i.type_of_skill, i.id
            FROM ideas i
            WHERE i.user_id = ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?"""
        
    elif search_skill_type != None and search_keyword != None:
         sql = """SELECT i.title, i.content, i.type_of_skill, i.id
            FROM ideas i
            WHERE i.user_id = ? AND i.type_of_skill = ? AND title LIKE ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?"""
         params.append(search_skill_type)
         params.append(f"%{search_keyword}%")

    elif search_skill_type != None:
         sql = """SELECT i.title, i.content, i.type_of_skill, i.id
            FROM ideas i
            WHERE i.user_id = ? AND i.type_of_skill = ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?"""
         params.append(search_skill_type)
    else:
         sql = """SELECT i.title, i.content, i.type_of_skill, i.id
            FROM ideas i
            WHERE i.user_id = ? AND title LIKE ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?"""
         params.append(f"%{search_keyword}%")
    params.extend([limit, offset])

    ideas = db.query(sql, params)
    return ideas

def get_private_ideas_count(search_keyword=None, search_skill_type=None)-> int:
    params = [session["user_id"]]
    if search_keyword is None and search_skill_type is None:
        sql = "SELECT COUNT(id) FROM ideas WHERE user_id = ?"
    elif search_keyword and search_skill_type:
        sql = "SELECT COUNT(id) FROM ideas WHERE user_id = ? AND type_of_skill = ? AND title LIKE ?"
        params.extend([search_skill_type, f"%{search_keyword}%"])
    elif search_skill_type:
        sql = "SELECT COUNT(id) FROM ideas WHERE user_id = ? AND type_of_skill = ?"
        params.append(search_skill_type)
    else:
        sql = "SELECT COUNT(id) FROM ideas WHERE user_id = ? AND title LIKE ?"
        params.append(f"%{search_keyword}%")
    return db.query(sql, params)[0][0]

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

def find_matches_by_skill_type(type_of_skill:str)-> list:
    return db.query("SELECT * FROM ideas WHERE type_of_skill LIKE ? AND user_id = ?", [f"%{type_of_skill}%", session["user_id"]])