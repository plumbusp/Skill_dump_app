import sqlite3
from flask import session
from flask import redirect, render_template, request, g
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import datetime

short_list_length = 3

def get_user(user_id):
    sql = """SELECT id, usernames, image IS NOT NULL has_image
             FROM log_in_info 
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_messages(user_id):
    sql = """SELECT m.id,
                m.thread_id,
                t.title thread_title,
                m.sent_at,
                m.content
         FROM threads t, messages m
         WHERE t.id = m.thread_id AND
               m.user_id = ?
         ORDER BY m.sent_at DESC"""
    return db.query(sql, [user_id])

def get_last_messages(user_id):
    sql ="""SELECT m.id,
                m.thread_id,
                t.title thread_title,
                m.sent_at,
                m.content
         FROM threads t, messages m
         WHERE t.id = m.thread_id AND
               m.user_id = ?
         ORDER BY m.sent_at DESC"""
    last_messages = db.query(sql, [user_id])
    if len(last_messages) < short_list_length:
        return last_messages
    else:
        return last_messages[:3]
    
def get_image(user_id):
    sql = "SELECT image FROM log_in_info WHERE id = ?"
    result = db.query_one(sql, [user_id])
    if not result:
        return None
    return result["image"]
    
def update_image(user_id, image):
    sql = "UPDATE log_in_info SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def add_type_of_skill(user_id:int, skill:str):
    sql = "INSERT INTO skill_types (name, user_id) VALUES (?,?)"
    db.execute(sql,[ skill, user_id])

def get_users_skills(user_id):
    sql = "SELECT name FROM skill_types WHERE user_id = ?"
    return db.query(sql, [user_id])