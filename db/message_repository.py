from datetime import datetime
from db.connection import get_connection

# This file only talks to the database (raw SQL).
# It does not decide WHEN to save a message or format any output -
# that decision-making belongs in controllers/message_controller.py


def insert(sender, content):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)",
        (sender, content, timestamp)
    )
    conn.commit()
    conn.close()


def find_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sender, content, timestamp FROM messages ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def find_by_id(msg_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sender, content, timestamp FROM messages WHERE id = ?", (msg_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update(msg_id, new_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET content = ? WHERE id = ?", (new_content, msg_id))
    conn.commit()
    conn.close()


def delete(msg_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
