import json
from pathlib import Path

def save(records, path="data.json"):
    Path(path).write_text(json.dumps(records, indent=2, ensure_ascii=False))
