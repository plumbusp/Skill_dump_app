import sqlite3
from flask import g
def create_app_tables():
    print("1 Success!")
    with open("schema.sql") as file:
        con = sqlite3.connect("database.db")
        con.executescript(file.read())
        con.close()
        print("Success!")

def get_connection():
    connection = sqlite3.connect("database.db")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.commit()
    connection.row_factory = sqlite3.Row
    g.connection = connection
    return connection

def close_current_connection():
    g.connection.close()

def execute(sql, params=[]):
    """ data base same to execute in and """
    connection = get_connection()
    cursor = connection.execute(sql, params)
    connection.commit()
    g.last_insert_id = cursor.lastrowid
    connection.close()
    print("Closed connection")

def last_insert_id():
    return g.last_insert_id    
    
def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def query_one(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchone()
    con.close()
    return result