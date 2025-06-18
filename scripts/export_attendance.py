import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#ensures project root is in sys.path

import os
import sqlite3

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

conn = sqlite3.connect(DB_PATH)

import pandas as pd
from utils.encryption_utils import decrypt

def export_to_excel():
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    rows = c.fetchall()

    decrypted = []
    for roll, date, time in rows:
        decrypted.append((decrypt(roll), date, time))

    df = pd.DataFrame(decrypted, columns=["Roll", "Date", "Time"])
    df.to_excel("Attendance_Report.xlsx", index=False)
    print("[INFO] Attendance exported to Excel.")
    conn.close()

if __name__ == "__main__":
    export_to_excel()
