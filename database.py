import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            port=3307,
            password="school",
            database="music_player"
        )
        return connection
    except Error as err:
        if err.errno == 1049:  # Database doesn't exist
            create_database()
            return get_db_connection()
        raise err

def create_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            port=3307,
            password="school"
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS music_player")
        cursor.execute("USE music_player")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create playlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                song_path VARCHAR(255) NOT NULL,
                song_name VARCHAR(255),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        
        # Create favorites table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                song_path VARCHAR(255) NOT NULL,
                song_name VARCHAR(255),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                rating INTEGER NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as err:
        print(f"Error creating database: {err}")
        raise err

def add_favorite_and_playlist(username, song_path):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Add to favorites
        cur.execute("""
            INSERT INTO favorites (username, song_path) 
            VALUES (%s, %s)
            """, (username, song_path))
        # Add to playlist
        cur.execute("""
            INSERT INTO playlists (username, song_path) 
            VALUES (%s, %s)
            """, (username, song_path))
        conn.commit()
    except Error as err:
        print(f"Error adding to favorites/playlist: {err}")
        raise err
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def save_review(username, rating, feedback):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (username, rating, feedback) 
            VALUES (%s, %s, %s)
            """, (username, rating, feedback))
        conn.commit()
    except Error as err:
        print(f"Error saving review: {err}")
        raise err
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    # Initialize database and tables
    create_database()
    print("Database initialized successfully")