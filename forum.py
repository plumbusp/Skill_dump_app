"""Public ideas or forum"""
import sqlite3
from flask import Flask, session
from flask import redirect, render_template, request, g
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import datetime

def get_threads():
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM threads t, messages m
             WHERE t.id = m.thread_id
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_thread(thread_id):
    sql = """SELECT * FROM threads WHERE id = ?"""
    result = db.query_one(sql, [thread_id])
    return result if result else None

def add_thread(title, initial_message):
    user_id = session["user_id"]
    db.execute("""INSERT INTO threads (title, user_id)
               VALUES (?,?)""", [title, user_id])
    thread_id = db.last_insert_id()
    g.lastthreadid = thread_id
    add_message_to_thread(initial_message, thread_id)

def add_message(content, thread_id, user_id):
    username = db.query_one("SELECT usernames FROM log_in_info WHERE id = ?", [user_id])["usernames"]
    sql = "INSERT INTO messages (content, sent_at, user_id, thread_id, username) VALUES (?, datetime('now'), ?, ?, ?)"
    db.execute(sql, [content, user_id, thread_id, username])

# def get_name(thread_id:int):
#     result = db.query_one("""SELECT title FROM threads WHERE id = ? """, [thread_id])
#     return result["title"]

def get_last_thread_id():
    return g.lastthreadid

def add_message_to_thread(content, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, username, thread_id)
             VALUES (?, datetime('now'), ?, ?, ?)"""
    print(f"Username {session["username"]}")
    db.execute(sql, [content, session["user_id"], session["username"], thread_id])

def get_messages(thread_id):
    sql = """SELECT messages.*, log_in_info.usernames AS username
        FROM messages
        JOIN log_in_info ON messages.user_id = log_in_info.id
        WHERE messages.thread_id = ?"""
    
    return db.query(sql, [thread_id])

def get_message(thread_id:int, message_id:int):
    sql = """SELECT * FROM messages 
    WHERE thread_id = ? AND id = ?"""
    return db.query_one(sql, [thread_id, message_id])

def update_message(thread_id:int, message_id:int, content:str):
    db.execute("""UPDATE messages SET content = ? 
   WHERE thread_id = ? AND id = ?""", [content, thread_id, message_id])
    
def delete_message(thread_id:int, message_id:int):
    db.execute("""DELETE FROM messages WHERE thread_id = ? AND id = ?""",
               [thread_id, message_id])
    
def find_matches(keyword: str):
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM threads t, messages m
             WHERE t.id = m.thread_id AND t.title LIKE ?
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql, [f"%{keyword}%"])

# def get_thread_id_from_message(message_id):
#     sql = """SELECT thread_id FROM messages WHERE messages.id = ?"""
#     result = db.query_one(sql, [message_id])
#     return result["thread_id"]
