"""JSON file storage for time entries."""

import json
import os
from typing import Optional
from pathlib import Path

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DATA_FILE = os.path.join(DATA_DIR, "entries.json")


def _ensure_file():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"entries": []}, f)


def _read_all() -> dict:
    _ensure_file()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _write_all(data: dict):
    _ensure_file()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_entries(year: int, month: int) -> list[dict]:
    data = _read_all()
    return [e for e in data["entries"] if e["year"] == year and e["month"] == month]


def get_all_entries() -> list[dict]:
    return _read_all()["entries"]


def add_entry(entry: dict) -> dict:
    data = _read_all()
    entry["id"] = _next_id(data["entries"])
    data["entries"].append(entry)
    _write_all(data)
    return entry


def update_entry(entry_id: int, updates: dict) -> Optional[dict]:
    data = _read_all()
    for i, e in enumerate(data["entries"]):
        if e["id"] == entry_id:
            data["entries"][i] = {**e, **updates, "id": entry_id}
            _write_all(data)
            return data["entries"][i]
    return None


def delete_entry(entry_id: int) -> bool:
    data = _read_all()
    original_len = len(data["entries"])
    data["entries"] = [e for e in data["entries"] if e["id"] != entry_id]
    if len(data["entries"]) < original_len:
        _write_all(data)
        return True
    return False


def _next_id(entries: list[dict]) -> int:
    if not entries:
        return 1
    return max(e["id"] for e in entries) + 1
