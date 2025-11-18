"""
Database models and functions for user accounts
"""
import sqlite3
import json
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "user_data_web"
DB_PATH = USER_DATA_DIR / "users.db"

def init_db():
    """Initialize the database"""
    # Ensure directory exists
    USER_DATA_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT,
            profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT,
            messages TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()


def create_user(email, password):
    """Create a new user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        c.execute(
            'INSERT INTO users (email, password_hash) VALUES (?, ?)',
            (email, password_hash)
        )
        
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return user_id
    except sqlite3.IntegrityError:
        return None  # User already exists


def verify_user(email, password):
    """Verify user credentials"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    
    if result and check_password_hash(result[1], password):
        return result[0]  # Return user_id
    return None


def get_user(user_id):
    """Get user data"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, email, api_key, profile FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'email': result[1],
            'api_key': result[2],
            'profile': json.loads(result[3]) if result[3] else None
        }
    return None


def update_api_key(user_id, api_key):
    """Update user's API key"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE users SET api_key = ? WHERE id = ?', (api_key, user_id))
    
    conn.commit()
    conn.close()


def update_profile(user_id, profile):
    """Update user's health profile"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    profile_json = json.dumps(profile)
    c.execute('UPDATE users SET profile = ? WHERE id = ?', (profile_json, user_id))
    
    conn.commit()
    conn.close()


def save_chat(user_id, chat_id, title, messages):
    """Save a chat for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    messages_json = json.dumps(messages)
    created_at = datetime.now().isoformat()
    
    c.execute('''
        INSERT OR REPLACE INTO chats (id, user_id, title, messages, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (chat_id, user_id, title, messages_json, created_at))
    
    conn.commit()
    conn.close()


def get_user_chats(user_id):
    """Get all chats for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, title, created_at 
        FROM chats 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    results = c.fetchall()
    conn.close()
    
    chats = []
    for row in results:
        chats.append({
            'id': row[0],
            'title': row[1],
            'created_at': row[2]
        })
    
    return chats


def get_chat(chat_id, user_id):
    """Get a specific chat"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, title, messages, created_at 
        FROM chats 
        WHERE id = ? AND user_id = ?
    ''', (chat_id, user_id))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'title': result[1],
            'messages': json.loads(result[2]),
            'created_at': result[3]
        }
    return None

