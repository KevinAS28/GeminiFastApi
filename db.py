import hashlib
import re

import sqlite3

def hashmd5(text):
    return (hashlib.md5(text.encode('utf-8'))).hexdigest()

def connect_db():
    conn = sqlite3.connect("users.db")
    return conn

def add_user_to_database(username, hashed_password):
    # for safe usernaame: only allow a-z, A-Z, 0-9, _-
    username = re.sub(r'[^a-z|^A-Z|^0-9|^\_|^\-]*', '', username)
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()


def get_user_from_database(username=None, token=None):
    conn = connect_db()
    cursor = conn.cursor()
    if not username is None:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    else:
        cursor.execute("SELECT * FROM users WHERE token = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            token TEXT NULL
            )""")
    conn.commit()
    conn.close()

def generate_access_token(username, password):
    token = hashmd5(username+password)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users set token=? where username=?", (token, username))
    conn.commit()
    conn.close()
    return token
    

create_user_table() 
