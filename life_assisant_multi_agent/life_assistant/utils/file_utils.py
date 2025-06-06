import json
import os
from pathlib import Path
from threading import Lock

_json_lock = Lock()

def read_json(path: str) -> dict:
    with _json_lock:
        p = Path(path)
        if not p.exists():
            return {}
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

def write_json(path: str, data: dict) -> None:
    with _json_lock:
        p = Path(path)
        # Ensure parent directory exists
        if not p.parent.exists():
            os.makedirs(p.parent, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# Test rapide (désactivé par défaut)
if __name__ == "__main__":
    test_path = "test.json"
    write_json(test_path, {"foo": 123})
    print(read_json(test_path))
    Path(test_path).unlink(missing_ok=True)
