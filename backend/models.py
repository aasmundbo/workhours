"""Data models and validation for time entries."""

import uuid
from datetime import datetime


def validate_time(time_str: str) -> bool:
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def create_entry(date: str, clock_in: str, clock_out: str, note: str = "") -> dict:
    if not validate_date(date):
        raise ValueError(f"Invalid date format: {date}. Use YYYY-MM-DD.")
    if not validate_time(clock_in):
        raise ValueError(f"Invalid time format: {clock_in}. Use HH:MM.")
    if not validate_time(clock_out):
        raise ValueError(f"Invalid time format: {clock_out}. Use HH:MM.")

    t_in = datetime.strptime(clock_in, "%H:%M")
    t_out = datetime.strptime(clock_out, "%H:%M")
    if t_out <= t_in:
        raise ValueError("Clock-out must be after clock-in.")

    hours = (t_out - t_in).total_seconds() / 3600

    return {
        "id": str(uuid.uuid4()),
        "date": date,
        "clock_in": clock_in,
        "clock_out": clock_out,
        "hours": round(hours, 2),
        "note": note,
    }


def compute_hours(clock_in: str, clock_out: str) -> float:
    t_in = datetime.strptime(clock_in, "%H:%M")
    t_out = datetime.strptime(clock_out, "%H:%M")
    return round((t_out - t_in).total_seconds() / 3600, 2)
