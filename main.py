import tkinter as tk
import subprocess
import sys

def run_script(script):
    subprocess.run([sys.executable, script])

root = tk.Tk()
root.geometry("400x350")
root.title("Secure Attendance System")

tk.Button(root, text="Register Student", width=25, command=lambda: run_script("scripts/register_student.py")).pack(pady=10)
tk.Button(root, text="Mark Attendance", width=25, command=lambda: run_script("scripts/mark_attendance.py")).pack(pady=10)
tk.Button(root, text="Export Attendance", width=25, command=lambda: run_script("scripts/export_attendance.py")).pack(pady=10)
tk.Button(root, text="Open Teacher Dashboard", width=25, command=lambda: run_script("scripts/teacher_dashboard.py")).pack(pady=10)

root.mainloop()
