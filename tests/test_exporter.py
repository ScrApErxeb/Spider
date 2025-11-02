from storage.exporter import export_json, export_csv, compress
from pathlib import Path

def test_export_json_and_csv(tmp_path):
    data = [{"title": "x", "url": "y", "content": "z"}]
    json_path = tmp_path / "data.json"
    csv_path = tmp_path / "data.csv"

    p1 = export_json(data)
    p2 = export_csv(data)
    assert Path(p1).exists()
    assert Path(p2).exists()

def test_compress(tmp_path):
    file_path = tmp_path / "data.json"
    file_path.write_text("{}")
    zip_path = compress(file_path)
    assert zip_path.exists()
    assert zip_path.suffix == ".zip"
