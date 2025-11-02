import sqlite3
import logging

class Database:
    def __init__(self, path="data.db"):
        self.path = path
        self.conn = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.path)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    content TEXT
                )
            """)
            self.conn.commit()
        return self.conn

    def save(self, record):
        conn = self.connect()
        cur = conn.cursor()

        # Si liste de tuples -> insertion multiple
        if isinstance(record, list) and all(isinstance(r, (list, tuple)) for r in record):
            cur.executemany(
                "INSERT INTO data (title, url, content) VALUES (?, ?, ?)",
                record
            )
            conn.commit()
            return len(record)

        # Si tuple unique
        elif isinstance(record, (list, tuple)) and len(record) == 3:
            cur.execute("INSERT INTO data (title, url, content) VALUES (?, ?, ?)", record)
            conn.commit()
            return 1

        # Si simple chaîne -> stocker dans content
        elif isinstance(record, str):
            cur.execute("INSERT INTO data (title, url, content) VALUES ('', '', ?)", (record,))
            conn.commit()
            return 1

        else:
            raise ValueError("Format d’enregistrement non pris en charge")

    def save_batch(self, records):
        conn = self.connect()
        if not records:
            self.logger.warning("Empty batch, nothing saved")
            return 0

        cur = conn.cursor()
        normalized = []
        for r in records:
            if isinstance(r, (list, tuple)) and len(r) == 3:
                normalized.append(tuple(r))
            else:
                normalized.append(("", "", str(r)))

        cur.executemany(
            "INSERT INTO data (title, url, content) VALUES (?, ?, ?)",
            normalized,
        )
        conn.commit()
        self.logger.info(f"Saved {len(records)} records in batch")
        return len(records)

    def load(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT title, url, content FROM data")
        return cur.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
