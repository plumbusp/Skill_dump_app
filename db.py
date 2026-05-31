import sqlite3
from flask import g
def create_app_tables():
    with open("schema.sql") as file:
        con = sqlite3.connect("database.db")
        con.executescript(file.read())
        con.close()

def get_connection():
    create_app_tables()
    connection = sqlite3.connect("database.db")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.commit()
    connection.row_factory = sqlite3.Row
    return connection

def execute(sql, params=[]):
    create_app_tables()
    """ data base same to execute in and """
    connection = get_connection()
    result = connection.execute(sql, params)
    connection.commit()
    g.last_insert_id = result.lastrowid
    connection.close()

def last_insert_id():
    return g.last_insert_id    
    
def query(sql, params=[]):
    create_app_tables()
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result