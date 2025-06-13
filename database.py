import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bmi_data.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()

    def add_user(self, username):
        try:
            self.cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_id(self, username):
        self.cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_bmi_record(self, username, weight, height, bmi, category):
        user_id = self.get_user_id(username)
        if not user_id:
            user_id = self.add_user(username)
        self.cursor.execute('''
            INSERT INTO bmi_records (user_id, weight, height, bmi, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, weight, height, bmi, category))
        self.conn.commit()

    def get_user_history(self, username):
        self.cursor.execute('''
            SELECT weight, height, bmi, category, recorded_at
            FROM bmi_records
            JOIN users ON bmi_records.user_id = users.id
            WHERE users.username = ?
            ORDER BY recorded_at DESC
        ''', (username,))
        return self.cursor.fetchall()

    def get_all_users(self):
        self.cursor.execute('SELECT username FROM users')
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close() 