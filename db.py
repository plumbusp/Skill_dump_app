import sqlite3
from flask import g

def get_connection():
    connection = sqlite3.connect("database.db")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.commit()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS log_in_info (
            username varchar(50) PRIMARY KEY,
            password varchar(10)
        );
                                """)
    connection.commit()
    connection.row_factory = sqlite3.Row
    return connection

def execute(sql, params=[]):
    """ data base same to execute in and """
    connection = get_connection()
    result = connection.execute(sql, params)
    connection.commit()
    g.last_insert_id = result.lastrowid
    connection.close()

def last_insert_id():
    return g.last_insert_id    
    
def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result