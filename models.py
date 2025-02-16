import sqlite3

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

DEFAULT_SETTINGS = {
    "new_width": 40,
    "aspect_ratio_adjust": 0.55,
    "upscale_factor": 2,
    "invert": 0,
    "gradient_mode": "Default"
}

class db_models:
    @staticmethod
    def create_tables():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                new_width INTEGER,
                aspect_ratio_adjust REAL,
                upscale_factor INTEGER,
                invert INTEGER,
                gradient_mode TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def insert_or_update_user(telegram_id, username, first_name, last_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, username, first_name, last_name))
        conn.commit()
        conn.close()

    @staticmethod
    def log_user_message(telegram_id, message_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_messages (telegram_id, message)
            VALUES (?, ?)
        """, (telegram_id, message_text))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_settings(telegram_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_settings WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        else:
            return None

    @staticmethod
    def create_default_user_settings(telegram_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO user_settings (telegram_id, new_width, aspect_ratio_adjust, upscale_factor, invert, gradient_mode)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            telegram_id,
            DEFAULT_SETTINGS["new_width"],
            DEFAULT_SETTINGS["aspect_ratio_adjust"],
            DEFAULT_SETTINGS["upscale_factor"],
            1 if DEFAULT_SETTINGS["invert"] else 0,
            DEFAULT_SETTINGS["gradient_mode"]
        ))
        conn.commit()
        conn.close()
        return db_models.get_user_settings(telegram_id)

    @staticmethod
    def update_user_setting(telegram_id, setting_name, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        if setting_name == "invert":
            # ذخیره به صورت عددی
            value = 1 if value else 0
        query = f"UPDATE user_settings SET {setting_name} = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?"
        cursor.execute(query, (value, telegram_id))
        conn.commit()
        conn.close()
