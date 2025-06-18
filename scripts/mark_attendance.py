import sys
import os
import sqlite3
import cv2
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.face_utils import find_matching_roll
from utils.encryption_utils import encrypt
from database.init_db import initialize_database

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

def mark_attendance():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cap = cv2.VideoCapture(0)

    already_marked = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        temp_path = "temp.jpg"
        cv2.imwrite(temp_path, frame)
        roll = find_matching_roll(temp_path)

        if roll and roll not in already_marked:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            encrypted_roll = encrypt(roll)

            # Check if attendance already exists for this roll & date
            c.execute("SELECT 1 FROM attendance WHERE roll = ? AND date = ?", (encrypted_roll, date_str))
            if c.fetchone():
                print(f"[INFO] Attendance already marked for {roll} today.")
                already_marked.add(roll)
            else:
                c.execute("INSERT INTO attendance (roll, date, time) VALUES (?, ?, ?)", (encrypted_roll, date_str, time_str))
                conn.commit()
                already_marked.add(roll)
                print(f"[INFO] Marked attendance for {roll} at {time_str} on {date_str}")

        cv2.imshow("Camera - Press 'q' to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    mark_attendance()
