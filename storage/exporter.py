import json
import csv
from pathlib import Path

def export_json(data, path="data.json"):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))

def export_csv(data, path="data.csv"):
    if not data:
        return
    keys = data[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def get_path(fmt):
    return f"data.{fmt}"

def compress(path):  # placeholder
    pass
