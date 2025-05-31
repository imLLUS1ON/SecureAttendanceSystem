import sqlite3

def initialize_database():
    conn = sqlite3.connect("attendance.db")
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
