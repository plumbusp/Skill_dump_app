"""Public ideas or forum"""
from flask import session
import db


def get_threads(page, page_size):
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
            FROM threads t, messages m
            WHERE t.id = m.thread_id
            GROUP BY t.id
            ORDER BY t.id DESC
            LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def thread_count() -> int:
    sql = """SELECT COUNT(id) AS count FROM threads"""
    return db.query_one(sql)["count"]

def get_thread(thread_id):
    sql = """SELECT t.id, t.title, t.user_id FROM threads AS t WHERE id = ?"""
    result = db.query_one(sql, [thread_id])
    return result if result else None

def add_thread(title, initial_message):
    user_id = session["user_id"]
    db.execute("""INSERT INTO threads (title, user_id)
        VALUES (?,?)""", [title, user_id])
    thread_id = db.last_insert_id()
    g.lastthreadid = thread_id
    add_message(initial_message, thread_id, user_id)

def add_message(content, thread_id, user_id):
    sql = "INSERT INTO messages (content, sent_at, user_id, thread_id) VALUES (?, datetime('now'), ?, ?)"
    db.execute(sql, [content, user_id, thread_id])

def get_last_thread_id():
    return g.lastthreadid

def get_messages(thread_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, log_in_info.usernames AS username
        FROM messages AS m
        JOIN log_in_info ON m.user_id = log_in_info.id
        WHERE m.thread_id = ?"""
    
    return db.query(sql, [thread_id])

def get_message(thread_id:int, message_id:int):
    sql = """SELECT m.id, m.content, m.user_id, log_in_info.usernames AS username
        FROM messages AS m
        JOIN log_in_info ON m.user_id = log_in_info.id
        WHERE m.thread_id = ? AND m.id = ?"""
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
