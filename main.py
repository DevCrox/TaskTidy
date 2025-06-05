import customtkinter as ctk
from PIL import Image, ImageTk
import sqlite3
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# -------------------- Database Setup --------------------
conn = sqlite3.connect(resource_path('data/datatasks.db'))
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL
    )
''')
conn.commit()

# -------------------- App Setup --------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.iconbitmap(resource_path("Assets/icon.ico"))
window_width = 400
window_height = 600
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2) - 15
app.geometry(f"{window_width}x{window_height}+{x}+{y}")
app.title("Todo List")

# -------------------- Task Storage --------------------
task_widgets = []
edit_frames = 0

def fetch_tasks():
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()

def refresh():
    # Clear old task widgets
    for widget in task_widgets:
        widget.destroy()
    task_widgets.clear()

    tasks = fetch_tasks()
    app.bind("<Return>", lambda event: add_task())
    
    for i, (task_id, task_text) in enumerate(tasks):
        row = ctk.CTkFrame(task_frame)
        row.pack(fill='x', pady=5, padx=5)

        task_label = ctk.CTkLabel(row, text=task_text, font=('Arial', 14), anchor='w')
        task_label.pack(side='left', padx=(5, 10), expand=True, fill='x')

        edit_btn = ctk.CTkButton(row, text="Edit", width=40, command=lambda tid=task_id: edit_task(tid))
        edit_btn.pack(side='right', padx=(5, 0))

        delete_btn = ctk.CTkButton(row, text="Delete", width=50, command=lambda tid=task_id: delete_task(tid))
        delete_btn.pack(side='right', padx=(5, 0))

        task_widgets.append(row)

def add_task():
    task = entry.get().strip()
    if task:
        cursor.execute("INSERT INTO tasks (description) VALUES (?)", (task,))
        conn.commit()
        entry.delete(0, ctk.END)
        refresh()
    else:
        print("No task entered.")

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    refresh()

def edit_task(task_id):
    global edit_frames
    edit_frames += 1

    cursor.execute("SELECT description FROM tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()

    if result:
        current_desc = result[0]
        edit_window = ctk.CTkToplevel(app)
        edit_window.title("Edit Task")
        edit_entry = ctk.CTkEntry(edit_window, width=250)
        edit_entry.insert(0, current_desc)
        edit_entry.pack(pady=20)

        # Smart placement and layout: alternate left/right and increase Y
        if edit_frames % 2 == 0:
            x = 150
        else:
            x = 920
        y = 70 * (edit_frames)
        edit_window.geometry(f"300x150+{x}+{y}")

        def save_edit():
            new_text = edit_entry.get().strip()
            if new_text:
                cursor.execute("UPDATE tasks SET description = ? WHERE id = ?", (new_text, task_id))
                conn.commit()
                refresh()
                edit_window.destroy()

        edit_window.bind("<Return>", lambda event: save_edit())
        save_btn = ctk.CTkButton(edit_window, text="Save", command=save_edit)
        save_btn.pack(pady=10)

def delete_all():
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    refresh()


# -------------------- UI Widgets --------------------
titleFont = ctk.CTkFont(family="Cooper Black", size=32, underline=True)
title = ctk.CTkLabel(app, text="Todo List", font=titleFont, fg_color="transparent")
title.pack(padx=20, pady=10)

task_frame = ctk.CTkScrollableFrame(app, width=360, height=400)
task_frame.pack(padx=10, pady=10)

entry = ctk.CTkEntry(app, placeholder_text="Task", width=300)
entry.pack(pady=10)

submit_btn = ctk.CTkButton(app, text="Save", font=('Cooper Black', 20), command=add_task)
submit_btn.pack(pady=10)

delete_all_btn = ctk.CTkButton(task_frame, text="Delete All", fg_color="red", command=delete_all)
delete_all_btn.pack(side='bottom', pady=10)


# Initial refresh
refresh()

# -------------------- Main Loop --------------------
app.mainloop()
