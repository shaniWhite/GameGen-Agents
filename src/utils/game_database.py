
import sqlite3
from datetime import datetime

DB_FILE = "generated_games.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_game(game_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO games (game_name, created_at)
        VALUES (?, ?)
    ''', (
        game_name,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
