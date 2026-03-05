"""JSON file storage for time entries."""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_PATH = os.environ.get("DATA_FILE", "/data/hours.json")


def _resolve_path(path: Optional[str] = None) -> str:
    return path or DEFAULT_PATH


def _ensure_file(path: Optional[str] = None) -> None:
    path = _resolve_path(path)
    Path(os.path.dirname(path) or ".").mkdir(parents=True, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"entries": []}, f)


def load_entries(path: Optional[str] = None) -> list[dict]:
    path = _resolve_path(path)
    _ensure_file(path)
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("entries", [])


def save_entries(entries: list[dict], path: Optional[str] = None) -> None:
    path = _resolve_path(path)
    _ensure_file(path)
    with open(path, "w") as f:
        json.dump({"entries": entries}, f, indent=2)


def add_entry(entry: dict, path: Optional[str] = None) -> dict:
    path = _resolve_path(path)
    entries = load_entries(path)
    entries.append(entry)
    save_entries(entries, path)
    return entry


def update_entry(entry_id: str, updates: dict, path: Optional[str] = None) -> Optional[dict]:
    path = _resolve_path(path)
    entries = load_entries(path)
    for i, entry in enumerate(entries):
        if str(entry.get("id")) == str(entry_id):
            entries[i] = {**entry, **updates, "id": entry.get("id")}
            save_entries(entries, path)
            return entries[i]
    return None


def delete_entry(entry_id: str, path: Optional[str] = None) -> bool:
    path = _resolve_path(path)
    entries = load_entries(path)
    filtered = [entry for entry in entries if str(entry.get("id")) != str(entry_id)]
    if len(filtered) == len(entries):
        return False
    save_entries(filtered, path)
    return True
