import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import font as tkfont, ttk
from database import get_db_connection, add_favorite_and_playlist,save_review
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT
from PIL import Image, ImageTk
import os
from io import BytesIO
import time
import threading

# ICON LOADER
def load_icon(name, size):
    path = f"assets/{name}.png"
    if os.path.exists(path):
        return ImageTk.PhotoImage(Image.open(path).resize(size))
    else:
        img = Image.new("RGB", size, color="grey")
        return ImageTk.PhotoImage(img)


# REVIEW FORM
def review_form(player, login_window, username):  # Add username parameter
    review_win = tk.Toplevel(player)
    review_win.title("Feedback Form")
    review_win.geometry("400x350")
    review_win.configure(bg="#1e1e1e")

    tk.Label(
        review_win, text="⭐ Rate Your Experience",
        font=("times new roman", 14, "bold"), fg="#00aaff", bg="#1e1e1e"
    ).pack(pady=(15, 10))

    rating = tk.IntVar(value=0)

    def update_stars(selected):
        for i in range(5):
            if i < selected:
                stars[i].config(text="★", fg="gold")
            else:
                stars[i].config(text="☆", fg="white")
        rating.set(selected)

    star_frame = tk.Frame(review_win, bg="#1e1e1e")
    star_frame.pack()
    stars = []
    for i in range(5):
        star = tk.Label(star_frame, text="☆", font=("Arial", 24), fg="white", bg="#1e1e1e", cursor="hand2")
        star.bind("<Button-1>", lambda e, i=i: update_stars(i + 1))
        star.pack(side=tk.LEFT, padx=5)
        stars.append(star)

    tk.Label(
        review_win, text="\n💬 Write your feedback below:",
        font=("times new roman", 11), fg="white", bg="#1e1e1e"
    ).pack()

    feedback_text = tk.Text(review_win, width=40, height=5, bg="#2a2a2a", fg="white", wrap="word")
    feedback_text.pack(pady=10)

    def submit_feedback():
        user_rating = rating.get()
        user_feedback = feedback_text.get("1.0", tk.END).strip()

        if user_rating == 0:
            messagebox.showwarning("Warning", "Please rate your experience!")
            return

        try:
            save_review(username, user_rating, user_feedback)
            messagebox.showinfo("Thank You!", f"⭐ You rated {user_rating}/5\n\nYour feedback has been saved!")
            review_win.destroy()
            player.destroy()
            login_window()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save review: {str(e)}")

    tk.Button(
        review_win, text="Submit", command=submit_feedback,
        bg="#00aaff", fg="white", font=("Helvetica", 11, "bold"), width=12, cursor="hand2"
    ).pack(pady=15)
# MUSIC PLAYER
def music_player_window(username, login_window_func):
    pygame.mixer.init()
    player = tk.Tk()
    player.title(f"Music Player - {username}")
    player.geometry("900x700")
    player.configure(bg="#1e1e1e")
    player.resizable(False, False)

    # Set fullscreen after login
    player.attributes("-fullscreen", True)

    title_font = tkfont.Font(family="Segoe UI", size=22, weight="bold")
    header_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    normal_font = tkfont.Font(family="Segoe UI", size=11)
    small_font = tkfont.Font(family="Segoe UI", size=10)

    def add_hover(w, base_bg, hover_bg):
        def on_enter(e):
            try: w.config(bg=hover_bg)
            except: pass
        def on_leave(e):
            try: w.config(bg=base_bg)
            except: pass
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)

    # ---------- GREETING ----------
    tk.Label(player, text="🎶 Music Player 🎶", font=title_font, fg="#00aaff", bg="#1e1e1e").pack(pady=(15, 5))
    tk.Label(player,text=f"Welcome {username}",font=("Segoe UI", 17, "bold"),fg="#ffffff",bg="#1e1e1e").pack(pady=(0, 25))

    # Icons
    icons = {
        "heart": load_icon("heart", (25, 25)),
        "prev": load_icon("prev", (40, 40)),
        "play": load_icon("play", (50, 50)),
        "pause": load_icon("pause", (50, 50)),
        "next": load_icon("next", (40, 40)),
        "remove": load_icon("remove", (25, 25))
    }
    player.icons = icons  # keep references

    # Fonts
    def load_font(name, size, bold=False, italic=False):
        return tkfont.Font(family=name, size=size, weight="bold" if bold else "normal", slant="italic" if italic else "roman")

    title_font = load_font("Arial", 22, bold=True)
    subtitle_font = load_font("Arial", 16)
    label_font = load_font("Segoe UI", 11)
    button_font = load_font("Segoe UI", 11, bold=True)
    small_font = load_font("Arial", 10)

    left_frame = tk.Frame(player, bg="#1e1e1e", bd=1, relief=tk.GROOVE, padx=8, pady=8)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=12)

    right_frame = tk.Frame(player, bg="#1e1e1e")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

    # Playlist label, search and box
    tk.Label(left_frame, text="Playlist", font=header_font, bg="#1e1e1e", fg="#00aaff").pack(anchor="w")
    
    breadcrumb_frame = tk.Frame(left_frame, bg="#1e1e1e")
    breadcrumb_frame.pack(fill=tk.X, pady=(6, 0))
    breadcrumb_label = tk.Label(breadcrumb_frame, text="All items", fg="white", bg="#1e1e1e", font=("Arial", 10))
    breadcrumb_label.pack(side=tk.LEFT, padx=(2,0))
    back_btn = tk.Button(breadcrumb_frame, text="Back", command=lambda: go_back(), bg="#444444", fg="white")
    back_btn.pack(side=tk.RIGHT, padx=(0,2))
    back_btn.config(state=tk.DISABLED)

    # Search entry
    search_var = tk.StringVar()
    search_frame = tk.Frame(left_frame, bg="#0f1720", padx=6, pady=4)
    search_frame.pack(fill=tk.X, pady=(8, 8))
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=normal_font,
                            fg="#cfe8ff", bg="#081216", insertbackground="#cfe8ff",
                            relief=tk.FLAT, highlightthickness=0)
    search_entry.pack(fill=tk.X)
    
    # placeholder
    placeholder = "Search songs, folders..."
    placeholder_color = "#6e8b96"
    active_color = "#cfe8ff"
    def _focus_in(e):
        if search_entry.get() == placeholder:
            search_entry.delete(0, tk.END)
            search_entry.config(fg=active_color)
    def _focus_out(e):
        if not search_entry.get().strip():
            search_entry.insert(0, placeholder)
            search_entry.config(fg=placeholder_color)
    search_entry.bind("<FocusIn>", _focus_in)
    search_entry.bind("<FocusOut>", _focus_out)
    search_entry.insert(0, placeholder)
    search_entry.config(fg=placeholder_color)

    # Playlist listbox with scrollbar; make it expand to fill left frame
    
    playlist_container = tk.Frame(left_frame, bg="#0f1720", bd=1, relief=tk.FLAT, padx=6, pady=6)
    playlist_container.pack(fill=tk.BOTH, expand=True)
    
    # style
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Playlist.Treeview",
                    background="#0f1720",
                    fieldbackground="#0f1720",
                    foreground="#e6eef9",
                    rowheight=36,
                    font=normal_font,
                    borderwidth=0)
    style.map("Playlist.Treeview", background=[("selected", "#00aaff")], foreground=[("selected", "white")])
    style.layout("Playlist.Treeview", [])

    # Compact metadata table style
    style.configure("Meta.Treeview",background="#11161a",fieldbackground="#11161a",foreground="#dbeeff",rowheight=20,font=(normal_font.actual("family"), 9),borderwidth=0)
    
    style.configure("Meta.Treeview.Heading",background="#0b2a36",foreground="#cfe8ff",font=(normal_font.actual("family"), 10, "bold"))
    style.map("Meta.Treeview", background=[("selected", "#0d566e")], foreground=[("selected", "white")])
    style.configure("Dark.Vertical.TScrollbar",troughcolor="#0b1320",background="#1b2633",arrowcolor="#90a4b7",gripcount=0,bordercolor="#0b1320",lightcolor="#0b1320",darkcolor="#0b1320")
    style.configure("Dark.Horizontal.TScale",troughcolor="#0b1320",background="#00aaff")

    # columns: title
    playlist_tv = ttk.Treeview(playlist_container, columns=("title", "meta"), show="tree", style="Playlist.Treeview", selectmode="browse")
    playlist_tv.column("#0", width=0, stretch=False)  # hide implicit column
    playlist_tv.column("title", anchor="w", width=260)
    playlist_tv.column("meta", anchor="w", width=120)
    playlist_tv.heading("title", text="Title")
    playlist_tv.heading("meta", text="Info")
    scrollbar = ttk.Scrollbar(playlist_container, orient=tk.VERTICAL, command=playlist_tv.yview, style="Dark.Vertical.TScrollbar")
    playlist_tv.configure(yscrollcommand=scrollbar.set)
    playlist_tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    current_view = []
    playlist_items = []
    current_folder = None
    song_metadata = {}

    # Helper functions
    def display_label_for_item(it, show_index=False):
        if it["type"] == "folder":
            return f"[Folder] {it['name']} ({len(it['songs'])})"
        else:
            p = it["path"]
            return p if p.startswith("http") else os.path.basename(p)

    def get_display_list():
        if current_folder is None:
            # treat placeholder as empty so initial view shows all items
            q_raw = search_var.get().strip()
            if q_raw == placeholder:
                q = ""
            else:
                q = q_raw.lower()
            result = []
            for it in playlist_items:
                if it["type"] == "folder":
                    name = it["name"].lower()
                    if q == "" or q in name or any(q in os.path.basename(s).lower() for s in it["songs"]):
                        result.append(it)
                else:
                    label = os.path.basename(it["path"]).lower() if not it["path"].startswith("http") else it["path"].lower()
                    if q == "" or q in label:
                        result.append(it)
            return result
        else:
            # inside folder: list files (respect placeholder as empty)
            q_raw = search_var.get().strip()
            if q_raw == placeholder:
                q = ""
            else:
                q = q_raw.lower()
            if q == "":
                return [{"type":"file","path":p} for p in current_folder["songs"]]
            else:
                return [{"type":"file","path":p} for p in current_folder["songs"] if q in os.path.basename(p).lower() or q in p.lower()]

    def update_display():
        for iid in playlist_tv.get_children():
            playlist_tv.delete(iid)
        items = get_display_list()
        nonlocal current_view
        current_view = items
        for i, it in enumerate(items):
            tag = "odd" if i % 2 == 0 else "even"
            if it["type"] == "folder":
                title = f"[Folder] {it['name']} ({len(it['songs'])})"
                meta = ""
            else:
                path = it["path"]
                meta_info = song_metadata.get(path) or get_metadata(path)
                title = meta_info.get("title") or os.path.basename(path)
                artist = meta_info.get("artist") or ""
                meta = artist
            playlist_tv.insert("", "end", iid=str(i), values=(title, meta), tags=(tag,))
        playlist_tv.tag_configure("odd", background="#0f1720")
        playlist_tv.tag_configure("even", background="#0b1320")
        if current_folder is None:
            back_btn.config(state=tk.DISABLED)
            breadcrumb_label.config(text="All items")
        else:
            back_btn.config(state=tk.NORMAL)
            breadcrumb_label.config(text=f"Folder: {current_folder['name']}")
        # Keep selection cleared
        for s in playlist_tv.selection():
            playlist_tv.selection_remove(s)
            
            
    def go_back():
        nonlocal current_folder
        current_folder = None
        search_var.set("")
        update_display()

    #METADATA & ART
    def load_default_image():
        try:
            img = Image.open("assets/default.png").resize((180, 180))
            return ImageTk.PhotoImage(img)
        except Exception:
            img = tk.PhotoImage(width=180, height=180)
            img.put("#00aaff", to=(0, 0, 180, 180))
            return img

    def get_metadata(path):
        if path in song_metadata:
            return song_metadata[path]

        artist, album, year, description, lyrics = "Unknown", "Unknown", "Unknown", None, None
        title = os.path.splitext(os.path.basename(path))[0] if (path and not path.startswith("http")) else (path or "Unknown")
        image_data = None

        if path and not path.startswith("http") and os.path.exists(path):
            try:
                id3 = None
                try:
                    id3 = ID3(path)
                except Exception:
                    id3 = None
                if id3:
                    if "TIT2" in id3 and hasattr(id3["TIT2"], "text"):
                        title = id3["TIT2"].text[0]
                    if "TPE1" in id3 and hasattr(id3["TPE1"], "text"):
                        artist = id3["TPE1"].text[0]
                    if "TALB" in id3 and hasattr(id3["TALB"], "text"):
                        album = id3["TALB"].text[0]
                    # Year: try TDRC then TYER
                    if "TDRC" in id3 and hasattr(id3["TDRC"], "text"):
                        year = str(id3["TDRC"].text[0])
                    elif "TYER" in id3 and hasattr(id3["TYER"], "text"):
                        year = str(id3["TYER"].text[0])
                    for frame in id3.values():
                        if isinstance(frame, APIC):
                            image_data = frame.data
                        if isinstance(frame, USLT):
                            lyrics = frame.text
                    description = f"Artist: {artist}\nAlbum: {album}\nYear: {year}"
                else:
                    audio = MP3(path, ID3=ID3)
                    tags = audio.tags
                    if tags:
                        if "TIT2" in tags and hasattr(tags["TIT2"], "text"):
                            title = tags["TIT2"].text[0]
                        if "TPE1" in tags and hasattr(tags["TPE1"], "text"):
                            artist = tags["TPE1"].text[0]
                        if "TALB" in tags and hasattr(tags["TALB"], "text"):
                            album = tags["TALB"].text[0]
                        if "TDRC" in tags and hasattr(tags["TDRC"], "text"):
                            year = str(tags["TDRC"].text[0])
                        elif "TYER" in tags and hasattr(tags["TYER"], "text"):
                            year = str(tags["TYER"].text[0])
                        for tag in tags.values():
                            if isinstance(tag, APIC):
                                image_data = tag.data
                            if isinstance(tag, USLT):
                                lyrics = tag.text
                        description = f"Artist: {artist}\nAlbum: {album}\nYear: {year}"
            except Exception:
                pass

        meta = {"artist": artist, "album": album, "year": year, "title": title,
                "image_data": image_data, "description": description, "lyrics": lyrics}
        song_metadata[path] = meta
        return meta

    def update_album_art(file_or_url):
        meta = get_metadata(file_or_url)
        if meta.get("image_data"):
            try:
                image = Image.open(BytesIO(meta["image_data"])).resize((180, 180))
                album_art_img = ImageTk.PhotoImage(image)
            except Exception:
                album_art_img = load_default_image()
        else:
            album_art_img = load_default_image()
        player.album_art_img_ref = album_art_img
        album_art.configure(image=album_art_img)
        album_art.image = album_art_img
        update_metadata_table(meta)

    album_art_img = load_default_image()
    # Keep a reference to album_art_img so it is not garbage collected
    player.album_art_img_ref = album_art_img
    album_art = tk.Label(right_frame, image=album_art_img, bg="#1e1e1e", width=180, height=180, relief=tk.RIDGE)
    album_art.image = album_art_img
    album_art.pack(pady=10)

    # Compact metadata table (Artist / Album / Year)
    meta_frame = tk.Frame(right_frame, bg="#1e1e1e")
    meta_frame.pack(fill=tk.X, pady=(4,6))
    meta_tv = ttk.Treeview(meta_frame, columns=("artist","album","year"), show="headings", style="Meta.Treeview", height=1)
    meta_tv.column("artist", anchor="w", width=180)
    meta_tv.column("album", anchor="w", width=200)
    meta_tv.column("year", anchor="center", width=60)
    meta_tv.heading("artist", text="Artist")
    meta_tv.heading("album", text="Album")
    meta_tv.heading("year", text="Year")
    meta_tv.pack(fill=tk.X, padx=(2,0))

    def update_metadata_table(meta):
        # meta is a dict from get_metadata() or None
        for r in meta_tv.get_children():
            meta_tv.delete(r)
        if not meta:
            # show placeholder
            meta_tv.insert("", "end", values=("", "", ""))
            return
        artist = meta.get("artist") or "Unknown"
        album = meta.get("album") or "Unknown"
        year = meta.get("year") or ""
        if len(artist) > 30: artist = artist[:27] + "…"
        if len(album) > 30: album = album[:27] + "…"
        meta_tv.insert("", "end", values=(artist, album, year))

    # SONG MANAGEMENT
    def add_folder():
        nonlocal playlist_items
        audio_ext = (".mp3", ".wav", ".ogg", ".flac")
        folder_path = filedialog.askdirectory(title="Select Folder Containing Songs")
        if not folder_path:
            return
        files_to_add = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(audio_ext):
                    files_to_add.append(os.path.join(root, file))
        if not files_to_add:
            messagebox.showinfo("No audio files", "No audio files found in the selected folder.")
            return
        folder_name = os.path.basename(folder_path)
        folder_item = {"type":"folder", "name":folder_name, "songs":[]}
        conn = get_db_connection()
        cursor = conn.cursor()
        for file in files_to_add:
            if file not in folder_item["songs"]:
                folder_item["songs"].append(file)
                try:
                    cursor.execute("INSERT INTO playlists (username, song_path) VALUES (%s, %s)", (username, file))
                except Exception:
                    pass
                song_metadata[file] = get_metadata(file)
        cursor.close()
        conn.commit()
        conn.close()
        playlist_items.append(folder_item)
        update_display()
        if folder_item["songs"]:
            update_album_art(folder_item["songs"][0])

    def add_songs():
        nonlocal playlist_items, current_folder
        files = filedialog.askopenfilenames(title="Select Songs", filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")])
        if not files:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        if current_folder is None:
            for file in files:
                if not any(it["type"]=="file" and it["path"]==file for it in playlist_items):
                    playlist_items.append({"type":"file","path":file})
                    try:
                        cursor.execute("INSERT INTO playlists (username, song_path) VALUES (%s, %s)", (username, file))
                    except Exception:
                        pass
                    song_metadata[file] = get_metadata(file)
                    update_album_art(file)
        else:
            for file in files:
                if file not in current_folder["songs"]:
                    current_folder["songs"].append(file)
                    try:
                        cursor.execute("INSERT INTO playlists (username, song_path) VALUES (%s, %s)", (username, file))
                    except Exception:
                        pass
                    song_metadata[file] = get_metadata(file)
        cursor.close()
        conn.commit()
        conn.close()
        update_display()

    def remove_song():
        nonlocal is_playing, current_idx, start_offset, playlist_items, current_folder
        sel = playlist_tv.selection()
        if not sel:
            return
        idx = int(sel[0])
        view_list = current_view
        item = view_list[idx]
        conn = get_db_connection()
        cursor = conn.cursor()
        if item["type"] == "file":
            file_path = item["path"]
            # remove from DB
            try:
                cursor.execute("DELETE FROM playlists WHERE username=%s AND song_path=%s", (username, file_path))
                conn.commit()
            except Exception:
                pass
            # remove from in-memory structures
            if current_folder is None:
                for i,it in enumerate(playlist_items):
                    if it["type"]=="file" and it["path"]==file_path:
                        del playlist_items[i]
                        break
            else:
                current_folder["songs"].remove(file_path)
            try:
                pygame.mixer.music.stop()
            except:
                pass
            is_playing = False
            current_idx = None
            start_offset = 0.0
            play_btn.config(image=icons["play"])
            elapsed_label.config(text="0:00")
            total_label.config(text="0:00")
            album_art_img = load_default_image()
            album_art.configure(image=album_art_img)
            album_art.image = album_art_img
            update_metadata_table(None)
            update_display()
        elif item["type"] == "folder":
            # Prompt to remove folder and its songs from the playlist (and DB rows)
            folder = item
            if not messagebox.askyesno("Remove Folder", f"Remove folder '{folder['name']}' and its songs from playlist?"):
                cursor.close()
                conn.close()
                return
            for f in folder["songs"]:
                try:
                    cursor.execute("DELETE FROM playlists WHERE username=%s AND song_path=%s", (username, f))
                except Exception:
                    pass
            conn.commit()
            # remove from playlist_items
            for i,it in enumerate(playlist_items):
                if it is folder:
                    del playlist_items[i]
                    break
            update_display()
        cursor.close()
        conn.close()

    # Buttons laying out
    btn_base = "#00aaff"
    btn_hover = "#0088cc"
    add_folder_btn = tk.Button(left_frame, text="Add Folder", width=22, command=add_folder,bg=btn_base, fg="white", font=normal_font, bd=0)
    add_folder_btn.pack(pady=(6, 4))
    add_songs_btn = tk.Button(left_frame, text="Add Song", width=22, command=add_songs,bg=btn_base, fg="white", font=normal_font, bd=0)
    add_songs_btn.pack(pady=(0, 6))
    remove_btn_left = tk.Button(left_frame, text="Remove", width=22, command=remove_song,bg=btn_base, fg="white", font=normal_font, bd=0)
    remove_btn_left.pack(pady=(0, 6))
    
    add_hover(add_folder_btn, btn_base, btn_hover)
    add_hover(add_songs_btn, btn_base, btn_hover)
    add_hover(remove_btn_left, btn_base, btn_hover)

    # PROGRESS BAR
    progress_frame = tk.Frame(right_frame, bg="#1e1e1e")
    progress_frame.pack(fill=tk.X, pady=(10, 5))
    elapsed_label = tk.Label(progress_frame, text="0:00", fg="white", bg="#1e1e1e")
    elapsed_label.pack(side=tk.LEFT, padx=5)
    progress_var = tk.DoubleVar()
    # styled ttk.Scale 
    progress_slider = ttk.Scale(progress_frame, variable=progress_var, from_=0, to=100,orient=tk.HORIZONTAL, length=520, style="Dark.Horizontal.TScale")
    progress_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,4), pady=6)

    total_label = tk.Label(progress_frame, text="0:00", fg="white", bg="#1e1e1e")
    total_label.pack(side=tk.RIGHT, padx=5)

    # --- CONTROLS ---
    controls_frame = tk.Frame(right_frame, bg="#1e1e1e")
    controls_frame.pack(pady=20)

    is_playing = False
    current_idx = None  # index in current displayed list
    start_offset = 0.0
    user_is_seeking = False

    def resolve_path_for_index(idx):
        if idx is None:
            return None
        if idx < 0 or idx >= len(current_view):
            return None
        it = current_view[idx]
        return it["path"] if it["type"] == "file" else None

    def toggle_favorite():
        sel = playlist_tv.selection()
        if not sel:
            messagebox.showwarning("Warning", "No song selected")
            return
        idx = int(sel[0])
        path = resolve_path_for_index(idx)
        if not path:
            messagebox.showwarning("Warning", "Select a song to favorite (not a folder)")
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM favorites WHERE username=%s AND song_path=%s", (username, path))
        if cursor.fetchone():
            cursor.execute("DELETE FROM favorites WHERE username=%s AND song_path=%s", (username, path))
            messagebox.showinfo("Removed", "Song removed from favorites ❤️")
            cursor.execute("DELETE FROM playlists WHERE username=%s AND song_path=%s", (username, path))
        else:
            add_favorite_and_playlist(username, path)
            messagebox.showinfo("Added", "Song added to favorites ❤️ and playlist")
        conn.commit()
        cursor.close()
        conn.close()

    def toggle_play_pause():
        nonlocal is_playing, current_idx, start_offset
        sel = playlist_tv.selection()
        if not sel:
            return
        idx = int(sel[0])
        path = resolve_path_for_index(idx)
        if path is None:
            # folder double-click to drill in
            folder = current_view[idx]
            if folder["type"] == "folder":
                open_folder(folder)
            return
        current_idx = idx
        if is_playing:
            try:
                pygame.mixer.music.pause()
            except:
                pass
            play_btn.config(image=icons["play"])
            is_playing = False
        else:
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.load(path)
                    try:
                        pygame.mixer.music.play(start=start_offset)
                    except TypeError:
                        pygame.mixer.music.play()
                        start_offset = 0.0
                    update_album_art(path)
                    try:
                        length = MP3(path).info.length if not path.startswith("http") else 0
                        total_label.config(text=f"{int(length // 60)}:{int(length % 60):02d}")
                    except:
                        total_label.config(text="0:00")
                play_btn.config(image=icons["pause"])
                is_playing = True
            except Exception as e:
                print("Play error:", e)

    def open_folder(folder_item):
        nonlocal current_folder
        current_folder = folder_item
        update_display()

    def next_song():
        nonlocal current_idx, start_offset, is_playing
        view_list = current_view
        if current_idx is None:
            for i,it in enumerate(view_list):
                if it["type"]=="file":
                    target = i
                    break
            else:
                return
        else:
            target = None
            for i in range(current_idx+1, len(view_list)):
                if view_list[i]["type"]=="file":
                    target = i
                    break
            if target is None:
                return
        path = resolve_path_for_index(target)
        if not path:
            return
        current_idx = target
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print("Next play error:", e)
        update_album_art(path)
        try:
            length = 0 if path.startswith("http") else MP3(path).info.length
            total_label.config(text=f"{int(length // 60)}:{int(length % 60):02d}")
        except:
            total_label.config(text="0:00")
        play_btn.config(image=icons["pause"])
        is_playing = True

    def prev_song():
        nonlocal current_idx, start_offset, is_playing
        view_list = current_view
        if current_idx is None:
            # set to last file in view
            target = None
            for i in range(len(view_list)-1, -1, -1):
                if view_list[i]["type"]=="file":
                    target = i
                    break
            if target is None:
                return
        else:
            target = None
            for i in range(current_idx-1, -1, -1):
                if view_list[i]["type"]=="file":
                    target = i
                    break
            if target is None:
                return
        path = resolve_path_for_index(target)
        if not path:
            return
        current_idx = target
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print("Prev play error:", e)
        update_album_art(path)
        try:
            length = 0 if path.startswith("http") else MP3(path).info.length
            total_label.config(text=f"{int(length // 60)}:{int(length % 60):02d}")
        except:
            total_label.config(text="0:00")
        play_btn.config(image=icons["pause"])
        is_playing = True

    heart_btn = tk.Button(controls_frame, image=icons["heart"], bd=0, bg="#1e1e1e", command=toggle_favorite,activebackground="#333333")
    heart_btn.pack(side=tk.LEFT, padx=15)
    add_hover(heart_btn, "#1e1e1e", "#2b2b2b")

    prev_btn = tk.Button(controls_frame, image=icons["prev"], command=prev_song, bd=0, bg="#1e1e1e",activebackground="#333333")
    prev_btn.pack(side=tk.LEFT, padx=15)
    add_hover(prev_btn, "#1e1e1e", "#2b2b2b")

    play_btn = tk.Button(controls_frame, image=icons["play"], command=toggle_play_pause, bd=0, bg="#1e1e1e",activebackground="#333333")
    play_btn.pack(side=tk.LEFT, padx=15)
    add_hover(play_btn, "#1e1e1e", "#2b2b2b")

    next_btn = tk.Button(controls_frame, image=icons["next"], command=next_song, bd=0, bg="#1e1e1e",activebackground="#333333")
    next_btn.pack(side=tk.LEFT, padx=15)
    add_hover(next_btn, "#1e1e1e", "#2b2b2b")

    remove_btn = tk.Button(controls_frame, image=icons["remove"], command=remove_song, bd=0, bg="#1e1e1e",activebackground="#333333")
    remove_btn.pack(side=tk.LEFT, padx=15)
    add_hover(remove_btn, "#1e1e1e", "#2b2b2b")

    # ---------- HELPERS FOR SEEKING ----------
    def on_slider_press(event):
        nonlocal user_is_seeking
        user_is_seeking = True

    def on_slider_release(event):
        nonlocal user_is_seeking, start_offset, is_playing, current_idx
        user_is_seeking = False
        if current_idx is None:
            sel = playlist_tv.selection()
            if sel:
                current_idx = int(sel[0])
            else:
                return
        path = resolve_path_for_index(current_idx)
        if not path:
            return
        try:
            length = 0 if path.startswith("http") else MP3(path).info.length
            pct = progress_var.get() / 100.0
            seek_time = max(0.0, min(length, pct * length))
            start_offset = seek_time
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(start=seek_time)
            except TypeError:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            is_playing = True
            play_btn.config(image=icons["pause"])
        except Exception as e:
            print("Seek error:", e)

    progress_slider.bind("<Button-1>", on_slider_press)
    progress_slider.bind("<ButtonRelease-1>", on_slider_release)

    def on_selection(event):
        nonlocal current_idx, start_offset
        sel = playlist_tv.selection()
        if sel:
            current_idx = int(sel[0])
            start_offset = 0.0
            path = resolve_path_for_index(current_idx)
            if path:
                try:
                    update_album_art(path)
                    length = 0 if path.startswith("http") else MP3(path).info.length
                    total_label.config(text=f"{int(length // 60)}:{int(length % 60):02d}")
                except:
                    total_label.config(text="0:00")
            else:
                # selected a folder: show folder info
                view_list = get_display_list()
                folder = view_list[current_idx]
                # show a short summary in the metadata table
                folder_meta = {"artist": f"Folder: {folder['name']}",
                            "album": f"{len(folder['songs'])} songs",
                            "year": ""}
                update_metadata_table(folder_meta)

    playlist_tv.bind("<<TreeviewSelect>>", on_selection)

    def on_tree_click(event):
        row = playlist_tv.identify_row(event.y)
        if row:
            playlist_tv.selection_set(row)
            playlist_tv.focus(row)
            on_selection(None)
        else:
            # clicked empty area
            for s in playlist_tv.selection():
                playlist_tv.selection_remove(s)

    playlist_tv.bind("<ButtonRelease-1>", on_tree_click)

    def on_double(event):
        sel = playlist_tv.selection()
        if not sel:
            return
        idx = int(sel[0])
        it = current_view[idx]
        if it["type"] == "folder":
            open_folder(it)
        else:
            # play the file
            path = it["path"]
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                update_album_art(path)
                play_btn.config(image=icons["pause"])
            except Exception as e:
                print("Play error:", e)

    playlist_tv.bind("<Double-1>", on_double)

    def update_progress():
        while True:
            if is_playing and current_idx is not None:
                try:
                    path = resolve_path_for_index(current_idx)
                    if path and pygame.mixer.music.get_busy():
                        pos = pygame.mixer.music.get_pos() / 1000.0
                        current_time = start_offset + pos
                        length = 0 if path.startswith("http") else MP3(path).info.length
                        if current_time > length:
                            current_time = length
                        elapsed_label.config(text=f"{int(current_time // 60)}:{int(current_time % 60):02d}")
                        if not user_is_seeking and length > 0:
                            progress_var.set((current_time / length) * 100)
                except Exception:
                    pass
            time.sleep(0.5)

    threading.Thread(target=update_progress, daemon=True).start()

    #  --LOAD PLAYLIST FROM DATABASE--
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT song_path FROM playlists WHERE username=%s", (username,))
    rows = cursor.fetchall()
    for row in rows:
        file = row[0]
        # append as top-level file items
        if not any(it["type"]=="file" and it["path"]==file for it in playlist_items):
            playlist_items.append({"type":"file","path":file})
            song_metadata[file] = get_metadata(file)
    cursor.close()
    conn.close()

    update_display()

    # Bind search updates
    def on_search_change(*a):
        update_display()
    search_var.trace_add("write", on_search_change)

    # MENU BAR
    menubar = tk.Menu(player)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Home", command=lambda: messagebox.showinfo("Home", "Welcome Home"))
    filemenu.add_command(label="Exit", command=lambda: review_form(player, login_window_func,username))
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Dynamic Music Player\nBy Vedant Trivedi(IU:2341230636), \nDeep Amlani(IU:2341230653),\nMeehir Patel(IU:2341230686)"))
    menubar.add_cascade(label="Help", menu=helpmenu)
    player.config(menu=menubar)
    player.mainloop()

# Main
if __name__ == "__main__":
    from login import login_window
    login_window()