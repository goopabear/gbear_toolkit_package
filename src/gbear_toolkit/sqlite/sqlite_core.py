import sqlite3


class SQLite():
    def __init__(self, abs_db_path: str):
        self.conn = sqlite3.connect(abs_db_path)   # path to your .sqlite / .db file
        self.cur = self.conn.cursor()