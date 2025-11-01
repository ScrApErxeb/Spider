from storage.exporter import export_json, export_csv
from pathlib import Path

def test_export_json(tmp_path):
    data = [{"title": "x"}]
    path = tmp_path / "test.json"
    export_json(data, path)
    assert path.exists()
    assert "x" in path.read_text()

def test_export_csv(tmp_path):
    data = [{"title": "y", "link": "z"}]
    path = tmp_path / "test.csv"
    export_csv(data, path)
    assert path.exists()
    assert "title" in path.read_text()
