import sqlite3
import logging
import os
from urllib.parse import urlparse, urlunparse


def normalize_url(url):
    """Nettoie et uniformise les URLs (supprime fragments, query, slash final, casse)."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        clean = parsed._replace(fragment="", query="")
        url = urlunparse(clean)
        if url.endswith("/"):
            url = url.rstrip("/")
        return url.lower()
    except Exception:
        return url


class Database:
    def __init__(self, path="data/data.db"):
        self.path = path
        self.conn = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Connexion à la base + création de la table si nécessaire."""
        if not self.conn:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.conn = sqlite3.connect(self.path)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    url TEXT UNIQUE,
                    content TEXT
                )
            """)
            self.conn.commit()
        return self.conn

    def save(self, record):
        """Sauvegarde un seul enregistrement (ou une liste)."""
        conn = self.connect()
        cur = conn.cursor()

        if isinstance(record, list) and all(isinstance(r, (list, tuple)) for r in record):
            normalized = [
                (r[0], normalize_url(r[1]), r[2]) for r in record if len(r) == 3
            ]
            cur.executemany(
                "INSERT OR IGNORE INTO data (title, url, content) VALUES (?, ?, ?)", normalized
            )
            conn.commit()
            return len(normalized)

        elif isinstance(record, (list, tuple)) and len(record) == 3:
            title, url, content = record
            url = normalize_url(url)
            cur.execute(
                "INSERT OR IGNORE INTO data (title, url, content) VALUES (?, ?, ?)",
                (title, url, content),
            )
            conn.commit()
            return 1

        elif isinstance(record, str):
            cur.execute(
                "INSERT OR IGNORE INTO data (title, url, content) VALUES ('', '', ?)",
                (record,),
            )
            conn.commit()
            return 1

        else:
            raise ValueError("Format d’enregistrement non pris en charge")

    def save_batch(self, records):
        """Sauvegarde en lot avec filtrage des doublons."""
        conn = self.connect()
        if not records:
            self.logger.warning("Empty batch, nothing saved")
            return 0

        cur = conn.cursor()
        normalized = []
        for r in records:
            if isinstance(r, (list, tuple)) and len(r) == 3:
                title, url, content = r
                url = normalize_url(url)
                normalized.append((title, url, content))
            else:
                normalized.append(("", "", str(r)))

        cur.executemany(
            "INSERT OR IGNORE INTO data (title, url, content) VALUES (?, ?, ?)", normalized
        )
        conn.commit()
        self.logger.info(f"Saved {len(normalized)} records (duplicates ignored)")
        return len(normalized)

    def load(self):
        """Récupère tout le contenu."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT title, url, content FROM data")
        return cur.fetchall()

    def close(self):
        """Ferme la connexion."""
        if self.conn:
            self.conn.close()
            self.conn = None
