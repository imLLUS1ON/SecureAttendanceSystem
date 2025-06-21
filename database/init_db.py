import os
import sqlite3

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Students table
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        section TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
    """)

    # Subjects table
    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # Attendance table with subject support
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        roll TEXT,
        date TEXT,
        time TEXT,
        subject TEXT,
        PRIMARY KEY (roll, date, subject)
    )
    """)

    # Class sessions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS class_sessions (
        date TEXT,
        section TEXT,
        PRIMARY KEY (date, section)
    )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Database initialized.")

if __name__ == "__main__":
    initialize_database()
