import sqlite3
import db

short_list_length = 3

def get_user(user_id):
    sql = """SELECT usernames, image IS NOT NULL has_image
        FROM log_in_info 
        WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def username_exists(username:str)-> bool:
    sql = "SELECT usernames FROM log_in_info WHERE usernames=?"
    result = db.query(sql, [username])
    return bool(result)

def get_username_password(username:str):
    sql = "SELECT passwords FROM log_in_info WHERE usernames=?"
    result = db.query(sql, [username])
    if result== []:
        return ""
    return result[0][0]

def get_messages(user_id):
    sql = """SELECT m.id, m.thread_id, t.title thread_title,
        m.sent_at, m.content
        FROM threads t, messages m
        WHERE t.id = m.thread_id AND m.user_id = ?
        ORDER BY m.sent_at DESC"""
    return db.query(sql, [user_id])

def get_last_messages(user_id):
    sql ="""SELECT m.id, m.thread_id, t.title thread_title,
        m.sent_at, m.content
        FROM threads t, messages m
        WHERE t.id = m.thread_id AND m.user_id = ?
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

def add_type_of_skill(user_id:int, skill:str)-> bool:
    sql = "INSERT INTO skill_types (names, user_id) VALUES (?,?)"
    try:
        db.execute(sql,[skill, user_id])
        return True
    except sqlite3.IntegrityError: # UNIQUE constraint violations
        db.close_current_connection()
        return False

def get_users_skills(user_id:int):
    sql = "SELECT names FROM skill_types WHERE user_id = ?"
    return db.query(sql, [user_id])

def get_total_skills(user_id:int)-> int:
    sql = "SELECT COUNT(id) count FROM ideas WHERE user_id = ?"
    return db.query_one(sql, [user_id])["count"]

def get_skill_stats(user_id: int) -> list:
    sql = """SELECT COALESCE(st.names, 'Uncategorized') skill_type_name, COUNT(i.id) total
        FROM ideas i
        LEFT JOIN skill_types st ON i.type_of_skill = st.names
        WHERE i.user_id = ?
        GROUP BY st.id
        ORDER BY total DESC"""
    result = list(db.query(sql, [user_id]))

    total_count = sum(int(row["total"]) for row in result)
    one_percent = 100 / total_count if total_count else 0

    return [
        f"{row['skill_type_name']} has {row['total']} appearances and is {one_percent * int(row['total']):.1f}% of all skills"
        for row in result
    ]