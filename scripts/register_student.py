import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import tkinter as tk
from tkinter import messagebox
import cv2
from utils.encryption_utils import encrypt
from database.init_db import initialize_database

# Construct absolute path to attendance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')

conn = sqlite3.connect(DB_PATH)

def register_student():
    def capture_image():
        roll = roll_entry.get()
        name = name_entry.get()
        section = section_entry.get()

        if not roll or not name or not section:
            messagebox.showerror("Error", "All fields are required.")
            return

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access the camera.")
            return

        print("[INFO] Press 's' to capture, 'q' to cancel...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame.")
                break

            cv2.imshow("Capture Student Image", frame)

            key = cv2.waitKey(1)
            if key == ord('s'):
                image_path = f"images/{roll}.jpg"
                cv2.imwrite(image_path, frame)
                print(f"[INFO] Image saved at {image_path}")
                break
            elif key == ord('q'):
                print("[INFO] Capture cancelled.")
                cap.release()
                cv2.destroyAllWindows()
                return

        cap.release()
        cv2.destroyAllWindows()

        # Save to database
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?)",
                  (encrypt(roll), encrypt(name), encrypt(section), image_path))
        conn.commit()

        messagebox.showinfo("Success", f"{name} registered successfully.")

    # GUI
    win = tk.Tk()
    win.title("Register Student")
    tk.Label(win, text="Roll Number").grid(row=0, column=0)
    tk.Label(win, text="Name").grid(row=1, column=0)
    tk.Label(win, text="Section").grid(row=2, column=0)
    
    roll_entry = tk.Entry(win)
    name_entry = tk.Entry(win)
    section_entry = tk.Entry(win)
    
    roll_entry.grid(row=0, column=1)
    name_entry.grid(row=1, column=1)
    section_entry.grid(row=2, column=1)

    tk.Button(win, text="Capture & Register", command=capture_image).grid(row=3, columnspan=2)
    win.mainloop()

if __name__ == "__main__":
    initialize_database()
    register_student()
