import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import pandas as pd
from utils.encryption_utils import decrypt

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

def export_to_excel():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Step 1: Load and decrypt student info
    c.execute("SELECT roll, name, section FROM students")
    students = {}
    for roll, name, section in c.fetchall():
        try:
            decrypted_roll = decrypt(roll)
            students[decrypted_roll] = (decrypt(name), decrypt(section))
        except:
            continue

    # Step 2: Load attendance and match with decrypted rolls
    c.execute("SELECT * FROM attendance")
    rows = c.fetchall()

    decrypted = []
    for roll, date, time, subject in rows:
        try:
            real_roll = decrypt(roll)
            name, section = students.get(real_roll, ("Unknown", "Unknown"))
            decrypted.append((real_roll, date, time, subject, name, section))
        except:
            continue

    # Step 3: Export to Excel
    df = pd.DataFrame(decrypted, columns=["Roll", "Date", "Time", "Subject", "Name", "Section"])
    df.sort_values(by=["Date", "Roll"], inplace=True)
    df.to_excel("Attendance_Report.xlsx", index=False)
    print("[INFO] Attendance exported to Excel.")

    conn.close()

if __name__ == "__main__":
    export_to_excel()
