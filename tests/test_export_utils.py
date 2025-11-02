import json
import csv
import zipfile
from pathlib import Path
from utils.export_utils import export_json, export_csv, compress, EXPORT_DIR

def test_export_json(tmp_path):
    data = [{"name": "Alice"}, {"name": "Bob"}]
    path = export_json(data)
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == data
    assert path.parent == EXPORT_DIR

def test_export_csv(tmp_path):
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    path = export_csv(data)
    assert path.exists()
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
    assert path.parent == EXPORT_DIR

def test_export_csv_empty():
    path = export_csv([])
    assert path.exists()
    assert path.stat().st_size == 0 or path.read_text() == ""

def test_compress_creates_zip():
    dummy = EXPORT_DIR / "dummy.txt"
    dummy.write_text("test")
    zip_path = compress(dummy)
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        assert "dummy.txt" in zf.namelist()
