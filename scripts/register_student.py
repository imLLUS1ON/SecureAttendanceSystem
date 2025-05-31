import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#ensures project root is in sys.path

import tkinter as tk
from tkinter import messagebox
import cv2
import os
import sqlite3
from utils.encryption_utils import encrypt
from database.init_db import initialize_database

def register_student():
    def capture_image():
        roll = roll_entry.get()
        name = name_entry.get()

        if not roll or not name:
            messagebox.showerror("Error", "All fields are required.")
            return

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Error", "Camera failure.")
            return

        image_path = f"images/{roll}.jpg"
        cv2.imwrite(image_path, frame)

        # Save to database
        conn = sqlite3.connect("database/attendance.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?)",
                  (encrypt(roll), encrypt(name), image_path))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"{name} registered successfully.")

    # GUI
    win = tk.Tk()
    win.title("Register Student")
    tk.Label(win, text="Roll Number").grid(row=0, column=0)
    tk.Label(win, text="Name").grid(row=1, column=0)

    roll_entry = tk.Entry(win)
    name_entry = tk.Entry(win)
    roll_entry.grid(row=0, column=1)
    name_entry.grid(row=1, column=1)

    tk.Button(win, text="Capture & Register", command=capture_image).grid(row=2, columnspan=2)
    win.mainloop()

if __name__ == "__main__":
    initialize_database()
    register_student()
