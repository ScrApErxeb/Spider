import sqlite3
from storage.database import Database
from storage.models import PageModel, to_dict, from_dict


def test_save_and_load(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(path=db_path)
    db.connect()
    records = [("title1", "url1", "content1"), ("title2", "url2", "content2")]
    n = db.save(records)
    assert n == 2
    rows = db.load()
    assert len(rows) == 2
    db.close()


def test_page_model_roundtrip():
    page = PageModel("t", "u", "c")
    d = to_dict(page)
    restored = from_dict(d)
    assert restored.title == "t"
    assert restored.url == "u"
    assert restored.content == "c"


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
