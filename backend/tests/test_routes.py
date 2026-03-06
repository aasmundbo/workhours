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

    def test_punch_out_rejects_12h_format(self, client):
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_out": "04:00 PM"})
        assert resp.status_code == 400

    def test_punch_out_before_punch_in(self, client):
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_out": "07:00"})
        assert resp.status_code == 400

    def test_edit_open_entry_clock_in(self, client):
        """Editing the clock_in of an open (not yet punched out) entry must succeed."""
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_in": "09:00", "clock_out": None})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["clock_in"] == "09:00"
        assert data["clock_out"] is None
        assert data["hours"] is None

    def test_edit_open_entry_rejects_12h_clock_in(self, client):
        punch_resp = client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        entry_id = punch_resp.get_json()["id"]
        resp = client.put(f"/api/entries/{entry_id}", json={"clock_in": "09:00 AM", "clock_out": None})
        assert resp.status_code == 400


class TestStatsAPI:
    def test_stats_with_open_entry(self, client):
        """Stats must not crash when an open (punch-in only) entry exists."""
        client.post("/api/entries", json={"date": "2025-03-10", "clock_in": "08:00"})
        resp = client.get("/api/stats?year=2025&month=3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_hours"] == 0  # open entry contributes nothing

    def test_stats_open_entry_excluded_from_hours(self, client):
        """Completed entries count; open entries do not."""
        _post_entry(client, date="2025-03-10", clock_in="08:00", clock_out="16:00")
        client.post("/api/entries", json={"date": "2025-03-11", "clock_in": "08:00"})  # open
        resp = client.get("/api/stats?year=2025&month=3")
        data = resp.get_json()
        assert data["total_hours"] == 8.0

    def test_stats_after_delete(self, client):
        """Deleting an entry is reflected immediately in stats."""
        id1 = _post_entry(client, date="2025-03-10").get_json()["id"]
        _post_entry(client, date="2025-03-11")
        client.delete(f"/api/entries/{id1}")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["total_hours"] == 8.0

    def test_stats_after_edit(self, client):
        """Editing an entry's times is reflected immediately in stats."""
        entry_id = _post_entry(client, date="2025-03-10", clock_in="08:00", clock_out="12:00").get_json()["id"]
        client.put(f"/api/entries/{entry_id}", json={"clock_in": "08:00", "clock_out": "16:00"})
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["total_hours"] == 8.0

    def test_stats_empty_month(self, client):
        """No completed entries → elapsed=0, expected=0, difference=0, on_track=True."""
        resp = client.get("/api/stats?year=2025&month=3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_hours"] == 0
        assert data["elapsed_workdays"] == 0
        assert data["difference"] == 0
        assert data["on_track"] is True

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

    # --- Week-level pace fields ---
    # January 2025 is used for week tests: last day is Jan 31 (Friday),
    # so the last ISO week 2025-W05 (Jan 27-31) is fully contained in January.
    # elapsed_workdays / week_elapsed_workdays are capped at the last completed entry.

    def test_stats_response_has_week_fields(self, client):
        """Response includes all week-level pace fields."""
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        for key in ("week_difference", "week_total_hours", "week_elapsed_workdays",
                    "week_target_so_far", "current_week"):
            assert key in data, f"Missing key: {key}"

    def test_week_current_key_past_month(self, client):
        """For a past month the current_week is the ISO week of the last day."""
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        # Jan 31, 2025 (Friday) belongs to 2025-W05
        assert data["current_week"] == "2025-W05"

    def test_week_elapsed_workdays_capped_at_last_completed(self, client):
        """week_elapsed_workdays reflects the last completed entry, not end-of-week."""
        # Log Mon-Thu in 2025-W05; last completed = Jan 30 (Thu) → 4 elapsed days
        for day in range(27, 31):  # Jan 27-30 (Mon-Thu)
            _post_entry(client, date=f"2025-01-{day:02d}")
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_elapsed_workdays"] == 4
        assert data["week_target_so_far"] == 32

    def test_week_elapsed_workdays_full_week(self, client):
        """All 5 days logged → 5 elapsed workdays and target of 40h."""
        for day in range(27, 32):  # Jan 27-31, 2025 (Mon-Fri = W05)
            _post_entry(client, date=f"2025-01-{day:02d}")
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_elapsed_workdays"] == 5
        assert data["week_target_so_far"] == 40

    def test_week_difference_no_entries(self, client):
        """No completed entries → week_elapsed=0, expected=0, week_difference=0."""
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_total_hours"] == 0.0
        assert data["week_elapsed_workdays"] == 0
        assert data["week_difference"] == 0.0

    def test_week_difference_fully_logged(self, client):
        """5×8h entries in the last ISO week → week_difference=0."""
        for day in range(27, 32):  # Jan 27-31, 2025 (Mon-Fri = 2025-W05)
            _post_entry(client, date=f"2025-01-{day:02d}")
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_total_hours"] == 40.0
        assert data["week_difference"] == 0.0

    def test_week_difference_ahead(self, client):
        """Logging more than 8h/day gives a positive week_difference."""
        for day in range(27, 32):  # Mon-Fri 2025-W05
            _post_entry(client, date=f"2025-01-{day:02d}", clock_in="08:00", clock_out="17:00")  # 9h each
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_total_hours"] == 45.0
        assert data["week_difference"] == 5.0

    def test_week_difference_behind(self, client):
        """Logging less than 8h/day gives a negative week_difference."""
        # 5h Mon + 8h Tue → 13h logged, 2 elapsed days, 16h expected → -3h
        _post_entry(client, date="2025-01-27", clock_in="09:00", clock_out="14:00")  # 5h
        _post_entry(client, date="2025-01-28", clock_in="09:00", clock_out="17:00")  # 8h
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_total_hours"] == 13.0
        assert data["week_elapsed_workdays"] == 2
        assert data["week_difference"] == -3.0

    def test_week_open_entry_does_not_extend_elapsed(self, client):
        """An open (punch-in only) entry on the next day does not advance week_elapsed_workdays."""
        _post_entry(client, date="2025-01-27")  # completed Mon
        # Open entry on Tue — should NOT push elapsed to 2
        client.post("/api/entries", json={"date": "2025-01-28", "clock_in": "08:00"})
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        assert data["week_elapsed_workdays"] == 1
        assert data["week_difference"] == 0.0  # 8h logged == 8h expected (1 day)

    def test_month_elapsed_capped_at_last_completed_day(self, client):
        """Month elapsed_workdays is capped at the last completed entry, not today/end-of-month."""
        # Log only Mon-Wed of first week in March 2025 (Mar 3-5)
        for day in range(3, 6):  # 3 days × 8h
            _post_entry(client, date=f"2025-03-{day:02d}")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        # last completed = Mar 5 (Wed) → 3 elapsed workdays, expected = 24h
        assert data["elapsed_workdays"] == 3
        assert data["expected_so_far"] == 24
        assert data["difference"] == 0.0

    def test_month_open_entry_does_not_extend_elapsed(self, client):
        """An open entry after the last completed day does not advance elapsed_workdays."""
        _post_entry(client, date="2025-03-03")  # completed Mon
        client.post("/api/entries", json={"date": "2025-03-04", "clock_in": "08:00"})  # open Tue
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["elapsed_workdays"] == 1
        assert data["difference"] == 0.0  # 8h logged == 8h expected

    def test_week_total_hours_matches_weekly_list(self, client):
        """week_total_hours in top-level stats matches the same week entry in 'weekly'."""
        _post_entry(client, date="2025-01-27")
        _post_entry(client, date="2025-01-28")
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        current_wk = data["current_week"]
        matching = next((w for w in data["weekly"] if w["week"] == current_wk), None)
        assert matching is not None
        assert matching["hours"] == data["week_total_hours"]

    def test_week_difference_unrelated_week_entries_excluded(self, client):
        """Entries outside the reference week do not affect week_total_hours or week_elapsed."""
        # Log hours in an earlier week only (2025-W01: Jan 2-3)
        _post_entry(client, date="2025-01-02")
        _post_entry(client, date="2025-01-03")
        resp = client.get("/api/stats?year=2025&month=1")
        data = resp.get_json()
        # current_week is 2025-W05 (Jan 27-31); those entries are in W01
        assert data["week_total_hours"] == 0.0
        assert data["week_elapsed_workdays"] == 0
        assert data["week_difference"] == 0.0


class TestWorkScheduleEnvVars:
    """Tests for WORK_HOURS_PER_WEEK / WORK_DAYS_PER_WEEK env var support.

    Uses March 2025 (Mon 3 – Fri 7 for week W10) and January 2025 W05 (Mon 27 – Fri 31).
    """

    def test_default_schedule_is_40h_5d(self, client):
        """Defaults produce 8h/day and 5-day weeks with no env vars set."""
        for day in range(3, 8):  # Mon-Fri Mar 3-7
            _post_entry(client, date=f"2025-03-{day:02d}")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["target_hours"] == 21 * 8  # March has 21 workdays
        assert data["hours_per_day"] == 8.0
        assert data["hours_per_week"] == 40.0
        assert data["work_days_per_week"] == 5
        # Weekly target in the weekly list
        w10 = next(w for w in data["weekly"] if w["week"] == "2025-W10")
        assert w10["target"] == 40.0

    def test_schedule_fields_in_response(self, client):
        """Response always includes hours_per_day, hours_per_week, work_days_per_week."""
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert "hours_per_day" in data
        assert "hours_per_week" in data
        assert "work_days_per_week" in data

    def test_custom_schedule_fields_in_response(self, client, monkeypatch):
        """Custom env vars are reflected in the schedule fields of the response."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "36")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["hours_per_week"] == 36.0
        assert data["work_days_per_week"] == 4
        assert data["hours_per_day"] == 9.0  # 36 / 4

    def test_custom_32h_4day_week_target(self, client, monkeypatch):
        """32h / 4-day week → 8h/day target, Friday excluded from workday count."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "32")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        # March 2025: Mon-Thu only (weekday < 4). Count Mon-Thu days in March.
        expected_workdays = sum(
            1 for d in range(1, 32)
            if __import__("datetime").datetime(2025, 3, d).weekday() < 4
        )
        assert data["total_workdays"] == expected_workdays
        assert data["target_hours"] == expected_workdays * 8.0  # 32h/4d = 8h/day

    def test_custom_schedule_excludes_friday(self, client, monkeypatch):
        """With WORK_DAYS_PER_WEEK=4, Fridays are not counted as workdays."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "32")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        # Log Mon-Fri (5 entries); Fri should not advance elapsed_workdays
        for day in range(3, 8):
            _post_entry(client, date=f"2025-03-{day:02d}")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        # last completed = Fri Mar 7, but Fri is not a workday → elapsed = Mon-Thu = 4
        assert data["elapsed_workdays"] == 4
        assert data["expected_so_far"] == 32.0  # 4 days × 8h

    def test_custom_schedule_difference_exact(self, client, monkeypatch):
        """Pace difference is computed with custom hours_per_day."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "20")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "5")
        # Log Mon only: 4h (half a 4h/day target)
        _post_entry(client, date="2025-03-03", clock_in="09:00", clock_out="13:00")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        assert data["elapsed_workdays"] == 1
        assert data["expected_so_far"] == 4.0   # 20h / 5d = 4h/day
        assert data["difference"] == 0.0        # 4h logged == 4h expected

    def test_custom_schedule_week_target_in_list(self, client, monkeypatch):
        """Weekly list entries carry the configured WORK_HOURS_PER_WEEK as their target."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "32")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        data = client.get("/api/stats?year=2025&month=3").get_json()
        for w in data["weekly"]:
            assert w["target"] == 32.0

    def test_custom_schedule_week_end_is_thursday(self, client, monkeypatch):
        """With WORK_DAYS_PER_WEEK=4, each week's end date is Thursday (Mon+3)."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "32")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        data = client.get("/api/stats?year=2025&month=1").get_json()
        # W05: Mon=Jan 27 → Thu=Jan 30
        w05 = next(w for w in data["weekly"] if w["week"] == "2025-W05")
        assert w05["end"] == "2025-01-30"

    def test_custom_week_elapsed_capped_at_last_completed(self, client, monkeypatch):
        """Week elapsed pays attention to the custom workday count (4d)."""
        monkeypatch.setenv("WORK_HOURS_PER_WEEK", "32")
        monkeypatch.setenv("WORK_DAYS_PER_WEEK", "4")
        # Log Mon-Wed of 2025-W05 → last completed Wed Jan 29 → 3 elapsed workdays
        for day in (27, 28, 29):
            _post_entry(client, date=f"2025-01-{day:02d}")
        data = client.get("/api/stats?year=2025&month=1").get_json()
        assert data["week_elapsed_workdays"] == 3
        assert data["week_target_so_far"] == 24.0  # 3 × 8h
        assert data["week_difference"] == 24.0 - 24.0
