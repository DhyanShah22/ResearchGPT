import sqlite3
from passlib.hash import bcrypt

def create_connection():
    return sqlite3.connect("users.db", check_same_thread=False)

def create_users_table():
    conn = create_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, name, email, password):
    conn = create_connection()
    hashed_password = bcrypt.hash(password)
    try:
        conn.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                     (username, name, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, name FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.verify(password, result[0]):
        return result[1]  # Return name
    return None

def create_documents_table():
    conn = create_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_chat_table():
    conn = create_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
def create_chat_session(username, session_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (username, session_name) VALUES (?, ?)", (username, session_name))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def get_user_sessions(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, session_name FROM chat_sessions WHERE username = ? ORDER BY created_at DESC", (username,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_chat_history_by_session(session_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message FROM chat_history
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))
    history = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": message} for role, message in history]


def log_document(username, filename):
    conn = create_connection()
    conn.execute("INSERT INTO documents (username, filename) VALUES (?, ?)", (username, filename))
    conn.commit()
    conn.close()

def log_chat(username, role, message, session_id):
    conn = create_connection()
    conn.execute("""
        INSERT INTO chat_history (username, role, message, session_id) 
        VALUES (?, ?, ?, ?)
    """, (username, role, message, session_id))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message FROM chat_history
        WHERE username = ?
        ORDER BY timestamp ASC
    """, (username,))
    history = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": message} for role, message in history]

def delete_chat_history(username):
    conn = create_connection()
    conn.execute("DELETE FROM chat_history WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def create_chat_sessions_table():
    conn = create_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
