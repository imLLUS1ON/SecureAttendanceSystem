import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#ensures project root is in sys.path


import sqlite3
import pandas as pd
from utils.encryption_utils import decrypt

def export_to_excel():
    conn = sqlite3.connect("database/attendance.db")
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
