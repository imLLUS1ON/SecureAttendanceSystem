import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#ensures project root is in sys.path


import cv2
import sqlite3
from datetime import datetime
from utils.face_utils import find_matching_roll
from utils.encryption_utils import encrypt
from database.init_db import initialize_database

def mark_attendance():
    conn = sqlite3.connect("database/attendance.db")
    c = conn.cursor()

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        temp_path = "temp.jpg"
        cv2.imwrite(temp_path, frame)
        roll = find_matching_roll(temp_path)

        if roll:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            c.execute("INSERT OR IGNORE INTO attendance VALUES (?, ?, ?)", (encrypt(roll), date_str, time_str))
            conn.commit()
            print(f"[INFO] Marked attendance for {roll}")

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    mark_attendance()
