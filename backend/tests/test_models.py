"""Tests for data models and validation."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import compute_hours, create_entry, validate_date, validate_time


class TestValidateTime:
    def test_valid_times(self):
        assert validate_time("08:30") is True
        assert validate_time("00:00") is True
        assert validate_time("23:59") is True

    def test_invalid_times(self):
        assert validate_time("25:00") is False
        assert validate_time("8:30") is False
        assert validate_time("abc") is False
        assert validate_time("") is False


class TestValidateDate:
    def test_valid_dates(self):
        assert validate_date("2025-01-15") is True
        assert validate_date("2025-12-31") is True

    def test_invalid_dates(self):
        assert validate_date("2025-13-01") is False
        assert validate_date("01-15-2025") is False
        assert validate_date("not-a-date") is False


class TestCreateEntry:
    def test_creates_valid_entry(self):
        entry = create_entry("2025-03-01", "09:00", "17:00", "Regular day")
        assert entry["date"] == "2025-03-01"
        assert entry["clock_in"] == "09:00"
        assert entry["clock_out"] == "17:00"
        assert entry["hours"] == 8.0
        assert entry["note"] == "Regular day"
        assert "id" in entry

    def test_half_day(self):
        entry = create_entry("2025-03-01", "09:00", "13:00")
        assert entry["hours"] == 4.0

    def test_rejects_invalid_date(self):
        with pytest.raises(ValueError, match="Invalid date"):
            create_entry("bad-date", "09:00", "17:00")

    def test_rejects_invalid_clock_in(self):
        with pytest.raises(ValueError, match="Invalid time"):
            create_entry("2025-03-01", "bad", "17:00")

    def test_rejects_invalid_clock_out(self):
        with pytest.raises(ValueError, match="Invalid time"):
            create_entry("2025-03-01", "09:00", "bad")

    def test_rejects_out_before_in(self):
        with pytest.raises(ValueError, match="Clock-out must be after"):
            create_entry("2025-03-01", "17:00", "09:00")

    def test_rejects_equal_times(self):
        with pytest.raises(ValueError, match="Clock-out must be after"):
            create_entry("2025-03-01", "09:00", "09:00")


class TestComputeHours:
    def test_standard_day(self):
        assert compute_hours("09:00", "17:00") == 8.0

    def test_partial(self):
        assert compute_hours("09:00", "12:30") == 3.5
