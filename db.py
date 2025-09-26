import sqlite3

# Connect to (or create) the database
def get_db_connection():
    conn = sqlite3.connect("fitness.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # rows act like dicts
    return conn

# Initialize tables
def init_db():
    conn = get_db_connection()
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # Workouts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            date TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)
    conn.commit()
    conn.close()
