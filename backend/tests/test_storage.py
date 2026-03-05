"""Tests for storage module."""

import json
import os
import tempfile

import pytest

# Adjust path so imports work
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from storage import add_entry, delete_entry, load_entries, save_entries, update_entry


@pytest.fixture
def tmp_file():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestLoadEntries:
    def test_creates_file_if_missing(self, tmp_file):
        entries = load_entries(tmp_file)
        assert entries == []
        assert os.path.exists(tmp_file)

    def test_reads_existing_entries(self, tmp_file):
        data = {"entries": [{"id": "1", "date": "2025-01-01"}]}
        with open(tmp_file, "w") as f:
            json.dump(data, f)
        entries = load_entries(tmp_file)
        assert len(entries) == 1
        assert entries[0]["id"] == "1"


class TestSaveEntries:
    def test_saves_and_loads(self, tmp_file):
        entries = [{"id": "a", "hours": 8}]
        save_entries(entries, tmp_file)
        loaded = load_entries(tmp_file)
        assert loaded == entries

    def test_overwrites_existing(self, tmp_file):
        save_entries([{"id": "1"}], tmp_file)
        save_entries([{"id": "2"}], tmp_file)
        loaded = load_entries(tmp_file)
        assert len(loaded) == 1
        assert loaded[0]["id"] == "2"


class TestAddEntry:
    def test_appends_entry(self, tmp_file):
        add_entry({"id": "1", "hours": 4}, tmp_file)
        add_entry({"id": "2", "hours": 6}, tmp_file)
        entries = load_entries(tmp_file)
        assert len(entries) == 2


class TestUpdateEntry:
    def test_updates_existing(self, tmp_file):
        add_entry({"id": "1", "hours": 4, "note": ""}, tmp_file)
        result = update_entry("1", {"hours": 8, "note": "updated"}, tmp_file)
        assert result["hours"] == 8
        assert result["note"] == "updated"
        assert result["id"] == "1"

    def test_returns_none_for_missing(self, tmp_file):
        result = update_entry("nonexistent", {"hours": 1}, tmp_file)
        assert result is None


class TestDeleteEntry:
    def test_deletes_existing(self, tmp_file):
        add_entry({"id": "1"}, tmp_file)
        assert delete_entry("1", tmp_file) is True
        assert load_entries(tmp_file) == []

    def test_returns_false_for_missing(self, tmp_file):
        assert delete_entry("nonexistent", tmp_file) is False
