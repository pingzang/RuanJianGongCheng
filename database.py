import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "game_data.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    #用户基本信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            coin INTEGER DEFAULT 100)''')
    #抽卡记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS gacha_history (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL,draw_time TEXT NOT NULL,draw_type TEXT NOT NULL,card_name TEXT NOT NULL,card_star INTEGER NOT NULL,card_color TEXT NOT NULL)''')
    #图鉴收集记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS collection (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL,card_name TEXT NOT NULL,card_star INTEGER NOT NULL,card_color TEXT NOT NULL,UNIQUE(username, card_name))''')
    #签到记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS sign_in (username TEXT PRIMARY KEY,last_sign_date TEXT NOT NULL)''')
    #保底计数表
    cursor.execute('''CREATE TABLE IF NOT EXISTS pity_count (username TEXT PRIMARY KEY,count INTEGER DEFAULT 0)''')
    #抽卡分析表
    cursor.execute('''CREATE TABLE IF NOT EXISTS gacha_stat (username TEXT PRIMARY KEY,total_draw INTEGER DEFAULT 0,ssr_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "用户名已存在！"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password_hash, created_at, coin) VALUES (?, ?, ?, 10)",
        (username, password_hash, datetime.now())
    )
    conn.commit()
    conn.close()
    return True, "注册成功！"

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False, "用户名不存在！"
    if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user["id"])
        )
        conn.commit()
        conn.close()
        return True, "登录成功！"
    else:
        conn.close()
        return False, "密码错误！"