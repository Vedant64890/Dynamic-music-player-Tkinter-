# LOGIN WINDOW
import tkinter as tk
from tkinter import messagebox
from database import get_db_connection
from player import music_player_window

def login_window():
    root = tk.Tk()
    root.title("Music Player Login")
    root.geometry("600x600")
    root.resizable(False, False)
    root.configure(bg="#b3e0ff")

    canvas = tk.Canvas(root, width=500, height=600, highlightthickness=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    for i in range(0, 370, 2):
        canvas.create_rectangle(0, i, 600, i + 2, fill="#b3e0ff", outline="")

    box_y = 0.55
    box_height = 270
    box_width = 340
    shadow = tk.Frame(root, bg="#a0c4d6")
    shadow.place(relx=0.5, rely=box_y + 0.01, anchor=tk.CENTER, width=box_width, height=box_height + 8)
    box = tk.Frame(root, bg="white", bd=0, highlightbackground="#b3e0ff", highlightthickness=2)
    box.place(relx=0.5, rely=box_y, anchor=tk.CENTER, width=box_width, height=box_height)

    title = tk.Label(root, text="Welcome to Music Player!!", font=("Segoe UI", 20, "bold"), bg="#b3e0ff", fg="#1a1a1a")
    title.place(relx=0.5, rely=0.13, anchor=tk.CENTER)
    box_title = tk.Label(box, text="Login", font=("Segoe UI", 15, "bold"), bg="white", fg="#1a1a1a")
    box_title.pack(pady=(18, 8))

    user_label = tk.Label(box, text="Username", bg="white", font=("Segoe UI", 11))
    user_label.pack()
    username_entry = tk.Entry(box, relief=tk.FLAT, font=("Segoe UI", 11))
    username_entry.pack(pady=2)

    pass_label = tk.Label(box, text="Password", bg="white", font=("Segoe UI", 11))
    pass_label.pack()
    password_entry = tk.Entry(box, show="*", relief=tk.FLAT, font=("Segoe UI", 11))
    password_entry.pack(pady=2)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "All fields required")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        if cursor.fetchone():
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            music_player_window(username, login_window)  # Modified to pass login_window function
        else:
            messagebox.showerror("Error", "Invalid credentials")
        cursor.close()
        conn.close()

    login_btn = tk.Button(box, text="Login", command=login, font=("Segoe UI", 11, "bold"), 
                        bg="#b3e0ff", fg="#0077cc", relief=tk.FLAT, 
                        activebackground="#0077cc", activeforeground="white", bd=0)
    login_btn.pack(pady=12, ipadx=10, ipady=2)

    register_link = tk.Label(box, text="Don't have an account? Register", fg="#0077cc", bg="white", cursor="hand2",
    font=("Segoe UI", 10, "underline"))
    register_link.pack(pady=(0, 5))

    def open_register():
        root.destroy()  # Destroy login window first
        try:
            from register import register_window
            register_window()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open register window: {e}")

    register_link.bind("<Button-1>", lambda e: open_register())
    root.mainloop()