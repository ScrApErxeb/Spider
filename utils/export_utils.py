import json
import csv
import zipfile
from datetime import datetime
from pathlib import Path

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

def get_path(fmt):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return EXPORT_DIR / f"export_{ts}.{fmt}"

def export_json(data):
    path = get_path("json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def export_csv(data):
    path = get_path("csv")
    if not data:
        # fichier vide garanti
        with open(path, "w", encoding="utf-8"):
            pass
        return path
    keys = list(data[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    return path

def compress(path):
    zip_path = path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, arcname=path.name)
    return zip_path
