from pathlib import Path
import json
import csv
import gzip
import shutil
from datetime import datetime
import logging
import zipfile


logger = logging.getLogger(__name__)

EXPORT_DIR = Path("exports")


def ensure_export_folder(folder: Path = EXPORT_DIR) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def export_json(data, folder: Path = EXPORT_DIR) -> Path:
    folder = ensure_export_folder(folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = folder / f"export_{timestamp}.json"

    with filename.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Exported JSON to {filename}")
    return filename


def export_csv(data, folder: Path = EXPORT_DIR) -> Path:
    folder = ensure_export_folder(folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = folder / f"export_{timestamp}.csv"

    if not data:
        filename.touch()
        logger.warning(f"Empty CSV export created at {filename}")
        return filename

    if isinstance(data[0], dict):
        keys = data[0].keys()
        with filename.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    else:
        with filename.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)

    logger.info(f"Exported CSV to {filename}")
    return filename


def compress(file_path: Path) -> Path:
    zip_path = file_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, arcname=file_path.name)
    logger.info(f"Compressed export: {zip_path}")
    return zip_path
