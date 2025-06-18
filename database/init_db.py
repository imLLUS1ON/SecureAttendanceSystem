import os
import sqlite3

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

conn = sqlite3.connect(DB_PATH)

def initialize_database():
    c = conn.cursor()

    # Students table
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
    """)

    # Attendance table
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        roll TEXT,
        date TEXT,
        time TEXT,
        PRIMARY KEY (roll, date)
    )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Database initialized.")

if __name__ == "__main__":
    initialize_database()
