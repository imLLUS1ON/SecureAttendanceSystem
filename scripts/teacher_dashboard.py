import tkinter as tk
from tkinter import ttk
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.init_db import initialize_database
from utils.encryption_utils import decrypt

# Absolute path to DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

def load_attendance_data():
    if not os.path.exists(DB_PATH):
        initialize_database()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    records = c.fetchall()
    conn.close()

    decrypted = []
    for roll, date, time in records:
        try:
            decrypted.append((decrypt(roll), date, time))
        except:
            decrypted.append(("Invalid", date, time))  # fallback if decryption fails

    return decrypted

def open_teacher_dashboard():
    win = tk.Tk()
    win.title("Teacher Dashboard")
    win.geometry("500x400")

    # Treeview for attendance data
    cols = ("Roll Number", "Date", "Time")
    tree = ttk.Treeview(win, columns=cols, show='headings')

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor='center')

    # Vertical scrollbar
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.pack(fill="both", expand=True)

    # Load and insert data
    for row in load_attendance_data():
        tree.insert("", "end", values=row)

    win.mainloop()

if __name__ == "__main__":
    initialize_database()
    open_teacher_dashboard()
