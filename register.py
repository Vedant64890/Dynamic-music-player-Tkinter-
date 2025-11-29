# REGISTER WINDOW
import tkinter as tk
from database import get_db_connection
from tkinter import messagebox

def register_window():
    reg_win = tk.Tk()
    reg_win.title("Register")
    reg_win.geometry("600x600")
    reg_win.resizable(False, False)
    reg_win.configure(bg="#b3e0ff")

    canvas = tk.Canvas(reg_win, width=500, height=600, highlightthickness=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    for i in range(0, 400, 2):
        canvas.create_rectangle(0, i, 600, i + 2, fill="#b3e0ff", outline="")

    box_y = 0.55
    box_height = 300
    box_width = 340
    shadow = tk.Frame(reg_win, bg="#a0c4d6")
    shadow.place(relx=0.5, rely=box_y + 0.01, anchor=tk.CENTER, width=box_width, height=box_height + 8)
    box = tk.Frame(reg_win, bg="white", bd=0, highlightbackground="#b3e0ff", highlightthickness=2)
    box.place(relx=0.5, rely=box_y, anchor=tk.CENTER, width=box_width, height=box_height)

    title = tk.Label(reg_win, text="Welcome to Music Player!!", font=("Segoe UI", 20, "bold"), bg="#b3e0ff",
    fg="#1a1a1a")
    title.place(relx=0.5, rely=0.13, anchor=tk.CENTER)
    box_title = tk.Label(box, text="Register", font=("Segoe UI", 15, "bold"), bg="white", fg="#1a1a1a")
    box_title.pack(pady=(18, 8))

    user_label = tk.Label(box, text="Username", bg="white", font=("Segoe UI", 11))
    user_label.pack()
    username_entry = tk.Entry(box, relief=tk.FLAT, font=("Segoe UI", 11))
    username_entry.pack(pady=2)

    pass_label = tk.Label(box, text="Password", bg="white", font=("Segoe UI", 11))
    pass_label.pack()
    password_entry = tk.Entry(box, show="*", relief=tk.FLAT, font=("Segoe UI", 11))
    password_entry.pack(pady=2)

    def register():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "All fields required")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            reg_win.destroy()
            _open_login_after_register()
        cursor.close()
        conn.close()

    register_btn = tk.Button(box, text="Register", command=register, font=("Segoe UI", 11, "bold"), bg="#b3e0ff",
    fg="#0077cc", relief=tk.FLAT, activebackground="#0077cc", activeforeground="white", bd=0)
    register_btn.pack(pady=12, ipadx=10, ipady=2)

    login_link = tk.Label(box, text="Already have an account? Login", fg="#0077cc", bg="white", cursor="hand2",
    font=("Segoe UI", 10, "underline"))
    login_link.pack(pady=(0, 5))
    login_link.bind("<Button-1>", lambda e: (reg_win.destroy(), _open_login_after_register()))

def _open_login_after_register():
    try:
        from login import login_window
    except ImportError:
        messagebox.showwarning("login error occured !.")
        return
    login_window()