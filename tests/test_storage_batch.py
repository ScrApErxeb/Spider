import os
import sqlite3
from storage.database import Database

def test_save_batch(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(path=db_path)

    records = ["alpha", "beta", "gamma"]
    db.save_batch(records)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT content FROM data ORDER BY id")
    rows = [r[0] for r in cur.fetchall()]

    assert rows == records
    db.close()
    conn.close()

def test_empty_batch(tmp_path):
    db_path = tmp_path / "empty.db"
    db = Database(path=db_path)
    db.save_batch([])
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM data")
    count = cur.fetchone()[0]
    assert count == 0
    db.close()
    conn.close()
