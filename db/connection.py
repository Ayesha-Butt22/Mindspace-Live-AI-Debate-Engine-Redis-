import sqlite3
from config.settings import DATABASE_NAME


def get_connection():
    """Open and return a fresh SQLite connection."""
    return sqlite3.connect(DATABASE_NAME)


def create_table():
    """Create the messages table if it doesn't already exist. Run once at startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
