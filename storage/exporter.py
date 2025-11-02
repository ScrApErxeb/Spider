import json
import csv
import zipfile
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _get_path(fmt: str) -> Path:
    return EXPORT_DIR / f"export_{_timestamp()}.{fmt}"


def export_json(data) -> Path:
    path = _get_path("json")
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Exported JSON → {path}")
    return path


def export_csv(data) -> Path:
    path = _get_path("csv")
    if not data:
        path.touch()
        logger.warning(f"Empty CSV export → {path}")
        return path

    if isinstance(data[0], dict):
        keys = data[0].keys()
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    else:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)

    logger.info(f"Exported CSV → {path}")
    return path


def compress(path: Path) -> Path:
    zip_path = path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, arcname=path.name)
    logger.info(f"Compressed file → {zip_path}")
    return zip_path
