import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import pandas as pd
from datetime import datetime
from utils.encryption_utils import decrypt, encrypt
from database.init_db import initialize_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')


def load_attendance(tree, subject_filter="", section_filter="", date_filter="", roll_filter=""):
    tree.delete(*tree.get_children())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT roll, name, section FROM students")
    student_map = {}
    for enc_roll, enc_name, enc_section in c.fetchall():
        try:
            decrypted_roll = decrypt(enc_roll)
            decrypted_name = decrypt(enc_name)
            decrypted_section = decrypt(enc_section)
            student_map[decrypted_roll] = (decrypted_name, decrypted_section)
        except:
            continue

    query = "SELECT * FROM attendance"
    params = []
    if subject_filter or date_filter:
        query += " WHERE 1=1"
        if subject_filter:
            query += " AND subject = ?"
            params.append(subject_filter)
        if date_filter:
            query += " AND date = ?"
            params.append(date_filter)

    query += " ORDER BY date ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    records = []
    for row in rows:
        try:
            decrypted_roll = decrypt(row[0])
            name, section = student_map.get(decrypted_roll, ("Unknown", "Unknown"))
            if section_filter and section != section_filter:
                continue
            if roll_filter and decrypted_roll != roll_filter:
                continue
            subject = row[3] if len(row) > 3 else "N/A"
            records.append((decrypted_roll, name, row[1], subject, row[0]))
        except:
            continue

    records.sort(key=lambda x: (x[2], int(x[0]) if x[0].isdigit() else x[0]))

    for decrypted_roll, name, date, subject, enc_roll in records:
        tree.insert("", "end", values=(decrypted_roll, name, date, subject), tags=(enc_roll,))


def export_selected_day(subject_str, date_str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT roll, name FROM students")
    student_map = {}
    for enc_roll, enc_name in c.fetchall():
        try:
            decrypted_roll = decrypt(enc_roll)
            decrypted_name = decrypt(enc_name)
            student_map[decrypted_roll] = decrypted_name
        except:
            continue

    c.execute("SELECT * FROM attendance WHERE date = ?", (date_str,))
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        try:
            decrypted_roll = decrypt(row[0])
            name = student_map.get(decrypted_roll, "Unknown")
            time = row[2]
            subject = row[3]
            data.append((decrypted_roll, name, time, subject))
        except:
            continue

    if not data:
        messagebox.showinfo("No Data", f"No attendance records found for {date_str}")
        return

    file_name = f"{subject_str or 'Attendance'}_{date_str}.xlsx"
    df = pd.DataFrame(data, columns=["Roll", "Name", "Time", "Subject"])
    df.to_excel(file_name, index=False)
    messagebox.showinfo("Exported", f"Attendance for {date_str} exported to {file_name}")


def show_attendance_percentage():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch subjects
    c.execute("SELECT DISTINCT subject FROM attendance")
    subjects = sorted([row[0] for row in c.fetchall() if row[0]])
    if not subjects:
        messagebox.showinfo("No Data", "No subjects found in attendance.")
        return

    # Decrypt student names
    c.execute("SELECT roll, name FROM students")
    name_map = {}
    for roll, name in c.fetchall():
        try:
            name_map[decrypt(roll)] = decrypt(name)
        except:
            continue

    # Window UI
    win = tk.Toplevel()
    win.title("Attendance Percentage")
    win.geometry("1300x600")

    filter_frame = tk.Frame(win)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Select Subject:").grid(row=0, column=0)
    subject_var = tk.StringVar(value=subjects[0])
    subject_menu = ttk.Combobox(filter_frame, textvariable=subject_var, values=subjects, state="readonly")
    subject_menu.grid(row=0, column=1, padx=10)

    tree = ttk.Treeview(win, columns=("Roll", "Name", "Subject", "Percentage"), show="headings")
    tree.heading("Roll", text="Roll Number")
    tree.heading("Name", text="Name")
    tree.heading("Subject", text="Subject")
    tree.heading("Percentage", text="Attendance %")
    tree.pack(fill=tk.BOTH, expand=True)

    def load_percentages():
        tree.delete(*tree.get_children())
        subject = subject_var.get()

        c.execute("SELECT COUNT(DISTINCT date) FROM attendance WHERE subject = ?", (subject,))
        total_sessions = c.fetchone()[0]

        if total_sessions == 0:
            messagebox.showinfo("No Data", f"No sessions found for subject: {subject}")
            return

        c.execute("SELECT roll, COUNT(*) FROM attendance WHERE subject = ? GROUP BY roll", (subject,))
        data = []
        for enc_roll, count in c.fetchall():
            try:
                roll = decrypt(enc_roll)
                name = name_map.get(roll, "Unknown")
                percent = round((count / total_sessions) * 100, 2)
                row = (roll, name, subject, f"{percent}%")
                data.append(row)
                tree.insert("", "end", values=row)
            except:
                continue

        # Save current data for export
        tree.data = data

    def export_percent_data():
        data = getattr(tree, "data", [])
        if not data:
            messagebox.showinfo("No Data", "No data to export. Load a subject first.")
            return
        df = pd.DataFrame(data, columns=["Roll", "Name", "Subject", "Attendance %"])
        df.to_excel(f"Attendance_Percent_{subject_var.get()}.xlsx", index=False)
        messagebox.showinfo("Exported", f"Exported to Attendance_Percent_{subject_var.get()}.xlsx")

    tk.Button(filter_frame, text="Load", command=load_percentages).grid(row=0, column=2, padx=10)
    tk.Button(filter_frame, text="Export to Excel", command=export_percent_data).grid(row=0, column=3, padx=5)

    # Auto load initial subject
    load_percentages()

def delete_selected(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "No records selected.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for item in selected:
        values = tree.item(item, "values")
        tags = tree.item(item, "tags")

        if not tags:
            messagebox.showerror("Error", "Encrypted roll not found in tag.")
            continue

        encrypted_roll = tags[0]
        date = values[2]
        subject = values[3] if len(values) > 3 else None

        try:
            c.execute("DELETE FROM attendance WHERE roll = ? AND date = ? AND subject = ?", (encrypted_roll, date, subject))
            conn.commit()
            tree.delete(item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    conn.close()


def mark_attendance(tree):
    mark_win = tk.Toplevel()
    mark_win.title("Mark Attendance")

    tk.Label(mark_win, text="Roll Number:").grid(row=0, column=0)
    roll_entry = tk.Entry(mark_win)
    roll_entry.grid(row=0, column=1)

    tk.Label(mark_win, text="Section:").grid(row=1, column=0)
    section_entry = tk.Entry(mark_win)
    section_entry.grid(row=1, column=1)

    tk.Label(mark_win, text="Subject:").grid(row=2, column=0)
    subject_entry = tk.Entry(mark_win)
    subject_entry.grid(row=2, column=1)

    def submit_attendance():
        roll = roll_entry.get()
        section = section_entry.get()
        subject = subject_entry.get()

        if not roll or not section or not subject:
            messagebox.showerror("Error", "All fields are required.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT roll, name, section FROM students")
        students = c.fetchall()

        matched_student = None
        for s_roll, s_name, s_section in students:
            try:
                if decrypt(s_roll) == roll and decrypt(s_section) == section:
                    matched_student = (s_roll, s_name)
                    break
            except:
                continue

        if not matched_student:
            messagebox.showerror("Error", "Student not found.")
            conn.close()
            return

        enc_roll, enc_name = matched_student
        name = decrypt(enc_name)
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        try:
            c.execute("INSERT OR IGNORE INTO attendance VALUES (?, ?, ?, ?)", (enc_roll, date_str, time_str, subject))
            conn.commit()
            messagebox.showinfo("Success", f"Attendance marked for {name}.")
            load_attendance(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Could not mark attendance: {e}")
        finally:
            conn.close()
            mark_win.destroy()

    tk.Button(mark_win, text="Submit", command=submit_attendance).grid(row=3, columnspan=2, pady=10)


def teacher_dashboard():
    initialize_database()
    win = tk.Tk()
    win.title("Teacher Dashboard")
    win.geometry("1100x550")

    filter_frame = tk.Frame(win)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Subject:").grid(row=0, column=0)
    subject_entry = tk.Entry(filter_frame)
    subject_entry.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Section:").grid(row=0, column=2)
    section_entry = tk.Entry(filter_frame)
    section_entry.grid(row=0, column=3, padx=5)

    tk.Label(filter_frame, text="Date:").grid(row=0, column=4)
    date_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
    date_entry.grid(row=0, column=5, padx=5)

    tk.Label(filter_frame, text="Roll:").grid(row=0, column=6)
    roll_entry = tk.Entry(filter_frame)
    roll_entry.grid(row=0, column=7, padx=5)

    tk.Button(filter_frame, text="Apply Filters", command=lambda: load_attendance(
        tree,
        subject_filter=subject_entry.get().strip(),
        section_filter=section_entry.get().strip(),
        date_filter=date_entry.get().strip(),
        roll_filter=roll_entry.get().strip()
    )).grid(row=0, column=8, padx=5)

    tk.Button(filter_frame, text="Export Selected Day", command=lambda: export_selected_day(
        subject_entry.get().strip(),
        date_entry.get().strip()
    )).grid(row=0, column=9, padx=5)

    tree = ttk.Treeview(win, columns=("Roll", "Name", "Date", "Subject"), show="headings")
    tree.heading("Roll", text="Roll Number")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Subject", text="Subject")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Delete Selected Attendance", command=lambda: delete_selected(tree)).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Mark Attendance (Now)", command=lambda: mark_attendance(tree)).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Refresh", command=lambda: load_attendance(tree)).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Show Attendance %", command=show_attendance_percentage).grid(row=0, column=3, padx=5)

    win.mainloop()


if __name__ == "__main__":
    teacher_dashboard()
