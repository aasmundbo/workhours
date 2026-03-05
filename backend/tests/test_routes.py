"""Tests for API routes."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storage
from app import create_app


@pytest.fixture
def tmp_file():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def client(tmp_file, monkeypatch):
    monkeypatch.setattr(storage, "DEFAULT_PATH", tmp_file)
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _post_entry(client, date="2025-03-10", clock_in="09:00", clock_out="17:00", note=""):
    return client.post(
        "/api/entries",
        json={"date": date, "clock_in": clock_in, "clock_out": clock_out, "note": note},
    )


class TestEntriesAPI:
    def test_create_entry(self, client):
        resp = _post_entry(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["date"] == "2025-03-10"
        assert data["hours"] == 8.0

    def test_create_invalid_entry(self, client):
        resp = client.post("/api/entries", json={"date": "bad"})
        assert resp.status_code == 400

    def test_create_no_body(self, client):
        resp = client.post("/api/entries", content_type="application/json")
        assert resp.status_code == 400

    def test_get_entries_empty(self, client):
        resp = client.get("/api/entries")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_get_entries_filtered_by_month(self, client):
        _post_entry(client, date="2025-03-10")
        _post_entry(client, date="2025-04-10")
        resp = client.get("/api/entries?year=2025&month=3")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["date"] == "2025-03-10"

    def test_get_entries_sorted(self, client):
        _post_entry(client, date="2025-03-15", clock_in="09:00", clock_out="12:00")
        _post_entry(client, date="2025-03-10", clock_in="09:00", clock_out="17:00")
        resp = client.get("/api/entries?year=2025&month=3")
        data = resp.get_json()
        assert data[0]["date"] == "2025-03-10"
        assert data[1]["date"] == "2025-03-15"

    def test_update_entry(self, client):
        resp = _post_entry(client)
        entry_id = resp.get_json()["id"]
        resp = client.put(
            f"/api/entries/{entry_id}",
            json={"clock_in": "10:00", "clock_out": "18:00", "note": "late start"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["clock_in"] == "10:00"
        assert data["hours"] == 8.0
        assert data["note"] == "late start"

    def test_update_nonexistent(self, client):
        resp = client.put("/api/entries/fake-id", json={"note": "x"})
        assert resp.status_code == 404

    def test_delete_entry(self, client):
        resp = _post_entry(client)
        entry_id = resp.get_json()["id"]
        resp = client.delete(f"/api/entries/{entry_id}")
        assert resp.status_code == 200
        assert client.get("/api/entries").get_json() == []

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/entries/fake-id")
        assert resp.status_code == 404

    def test_delete_open_entry(self, client):
        """An open (punch-in only) entry can be deleted."""
        resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = resp.get_json()["id"]
        resp = client.delete(f"/api/entries/{entry_id}")
        assert resp.status_code == 200
        assert client.get("/api/entries").get_json() == []

    def test_delete_only_target_entry(self, client):
        """Deleting one entry leaves other entries untouched."""
        id1 = _post_entry(client, date="2025-03-10").get_json()["id"]
        id2 = _post_entry(client, date="2025-03-11").get_json()["id"]
        client.delete(f"/api/entries/{id1}")
        remaining = client.get("/api/entries").get_json()
        assert len(remaining) == 1
        assert remaining[0]["id"] == id2

    def test_delete_reduces_stats(self, client):
        """Deleting an entry is reflected in stats total hours."""
        id1 = _post_entry(client, date="2025-03-10").get_json()["id"]
        _post_entry(client, date="2025-03-11")
        client.delete(f"/api/entries/{id1}")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["total_hours"] == 8.0


class TestPunchInOut:
    def test_punch_in_creates_open_entry(self, client):
        resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["clock_in"] == "08:00"
        assert data["clock_out"] is None
        assert data["hours"] is None

    def test_punch_in_missing_clock_in(self, client):
        resp = client.post("/api/entries", json={"date": "2025-03-10"})
        assert resp.status_code == 400

    def test_open_entry_returned_in_list(self, client):
        client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        resp = client.get("/api/entries?year=2025&month=3")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["clock_out"] is None

    def test_punch_out_completes_open_entry(self, client):
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_out": "16:00"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["clock_out"] == "16:00"
        assert data["hours"] == 8.0

    def test_punch_out_nonexistent(self, client):
        resp = client.put("/api/entries/fake-id", json={"clock_out": "16:00"})
        assert resp.status_code == 404

    def test_punch_out_before_punch_in(self, client):
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_out": "07:00"})
        assert resp.status_code == 400


class TestStatsAPI:
    def test_stats_empty_month(self, client):
        resp = client.get("/api/stats?year=2025&month=3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_hours"] == 0
        assert data["on_track"] is False

    def test_stats_with_entries(self, client):
        # Add 5 days of 8h in March 2025 (first week)
        for day in range(3, 8):  # Mon-Fri March 3-7
            _post_entry(client, date=f"2025-03-{day:02d}")
        resp = client.get("/api/stats?year=2025&month=3")
        data = resp.get_json()
        assert data["total_hours"] == 40.0
        assert data["year"] == 2025
        assert data["month"] == 3
        assert len(data["weekly"]) > 0

    def test_stats_default_month(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "year" in data
        assert "month" in data

    def test_weekly_breakdown(self, client):
        _post_entry(client, date="2025-03-03")  # Monday
        _post_entry(client, date="2025-03-10")  # Next Monday
        resp = client.get("/api/stats?year=2025&month=3")
        data = resp.get_json()
        weeks_with_hours = [w for w in data["weekly"] if w["hours"] > 0]
        assert len(weeks_with_hours) == 2
