import sqlite3
import logging

class Database:
    def __init__(self, path="data.db"):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, content TEXT)"
        )
        self.conn.commit()

    def save(self, record):
        self.cursor.execute("INSERT INTO data (content) VALUES (?)", (record,))
        self.conn.commit()

    def save_batch(self, records):
        if not records:
            return
        data = [(r,) for r in records]
        self.cursor.executemany("INSERT INTO data (content) VALUES (?)", data)
        self.conn.commit()
        self.logger.debug(f"Batch insert {len(records)} rows")

    def load(self, query="SELECT * FROM data"):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
