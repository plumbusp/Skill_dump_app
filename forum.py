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

def add_thread(title, initial_message):
    user_id = session["user_id"]
    db.execute("""INSERT INTO threads (title, user_id)
               VALUES (?,?)""", [title, user_id])
    thread_id = db.last_insert_id()
    g.lastthreadid = thread_id
    add_message_to_thread(initial_message, thread_id)

def get_name(thread_id:int):
    title = db.query_one("""SELECT title FROM threads WHERE id = ? """, [thread_id])
    print(f"title {title}")
    return title["title"]

def get_last_thread_id():
    return g.lastthreadid

def add_message_to_thread(content, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, thread_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, session["user_id"], thread_id])

def get_messages(thread_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, l.usernames
             FROM messages m, log_in_info l
             WHERE m.user_id = l.id AND m.thread_id = ?
             ORDER BY m.id"""
    return db.query(sql, [thread_id])
