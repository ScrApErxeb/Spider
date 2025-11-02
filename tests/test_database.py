from storage.database import Database

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
