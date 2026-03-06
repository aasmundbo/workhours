"""Statistics and aggregation routes."""

import os
from collections import defaultdict
from datetime import datetime, timedelta
from calendar import monthrange

from flask import Blueprint, jsonify, request

from storage import load_entries

stats_bp = Blueprint("stats", __name__)


def _get_work_schedule() -> tuple[float, int, float]:
    """Read schedule env vars and return (hours_per_week, work_days_per_week, hours_per_day)."""
    hours_per_week = float(os.environ.get("WORK_HOURS_PER_WEEK", "40"))
    work_days_per_week = int(os.environ.get("WORK_DAYS_PER_WEEK", "5"))
    work_days_per_week = max(1, min(work_days_per_week, 5))  # clamp to 1-5
    hours_per_day = hours_per_week / work_days_per_week
    return hours_per_week, work_days_per_week, hours_per_day


def _is_workday(d: datetime, work_days_per_week: int) -> bool:
    """Return True if d is one of the first work_days_per_week days of the week (Mon onwards)."""
    return d.weekday() < work_days_per_week


def _get_iso_week(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _weeks_in_month(year: int, month: int, hours_per_week: float, work_days_per_week: int) -> dict:
    """Return all ISO weeks that overlap with the given month."""
    _, num_days = monthrange(year, month)
    weeks = {}
    for day in range(1, num_days + 1):
        d = datetime(year, month, day)
        iso = d.isocalendar()
        week_key = f"{iso[0]}-W{iso[1]:02d}"
        if week_key not in weeks:
            monday = d - timedelta(days=d.weekday())
            last_workday = monday + timedelta(days=work_days_per_week - 1)
            weeks[week_key] = {
                "week": week_key,
                "start": monday.strftime("%Y-%m-%d"),
                "end": last_workday.strftime("%Y-%m-%d"),
                "hours": 0.0,
                "target": hours_per_week,
            }
    return weeks


@stats_bp.route("/api/stats", methods=["GET"])
def get_stats():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if not year or not month:
        now = datetime.now()
        year = year or now.year
        month = month or now.month

    hours_per_week, work_days_per_week, hours_per_day = _get_work_schedule()

    entries = load_entries()
    month_entries = [
        e for e in entries if e["date"].startswith(f"{year:04d}-{month:02d}")
    ]

    # Total hours this month — open entries have hours=None, treat as 0
    total_hours = sum((e.get("hours") or 0) for e in month_entries)

    # Hours per day
    daily = defaultdict(float)
    for e in month_entries:
        daily[e["date"]] += (e.get("hours") or 0)

    # Hours per week
    weeks = _weeks_in_month(year, month, hours_per_week, work_days_per_week)
    for e in month_entries:
        wk = _get_iso_week(e["date"])
        if wk in weeks:
            weeks[wk]["hours"] += (e.get("hours") or 0)

    week_list = sorted(weeks.values(), key=lambda w: w["week"])

    # Working days info
    _, num_days = monthrange(year, month)
    total_workdays = sum(
        1
        for d in range(1, num_days + 1)
        if _is_workday(datetime(year, month, d), work_days_per_week)
    )

    today = datetime.now()

    # Elapsed workdays: count up to the last day that has a completed entry
    # (both clock_in and clock_out). Open/in-progress entries are excluded so
    # an active punch-in does not falsely inflate the "expected" hours target.
    completed_dates_month = sorted(
        e["date"] for e in month_entries
        if e.get("clock_in") and e.get("clock_out")
    )
    if completed_dates_month:
        last_completed = datetime.strptime(completed_dates_month[-1], "%Y-%m-%d")
        elapsed_workdays = sum(
            1
            for d in range(1, last_completed.day + 1)
            if _is_workday(datetime(year, month, d), work_days_per_week)
        )
    else:
        elapsed_workdays = 0

    target_hours = total_workdays * hours_per_day
    expected_so_far = elapsed_workdays * hours_per_day
    difference = total_hours - expected_so_far

    # Week-level comparison: use current week if viewing current month,
    # otherwise use the ISO week containing the last day of the viewed month.
    if today.year == year and today.month == month:
        ref_day = today
    else:
        ref_day = datetime(year, month, num_days)

    current_week_key = _get_iso_week(ref_day.strftime("%Y-%m-%d"))

    week_difference = 0.0
    week_total_hours = 0.0
    week_elapsed_workdays = 0
    week_target_so_far = 0.0

    if current_week_key in weeks:
        w = weeks[current_week_key]
        week_total_hours = w["hours"]
        week_start = datetime.strptime(w["start"], "%Y-%m-%d")

        # Count elapsed week days up to the last completed entry in this week.
        week_completed_dates = sorted(
            e["date"] for e in month_entries
            if e.get("clock_in") and e.get("clock_out")
            and _get_iso_week(e["date"]) == current_week_key
        )
        if week_completed_dates:
            week_cutoff = datetime.strptime(week_completed_dates[-1], "%Y-%m-%d")
            week_elapsed_workdays = sum(
                1
                for i in range(work_days_per_week)
                if (week_start + timedelta(days=i)) <= week_cutoff
            )
        else:
            week_elapsed_workdays = 0

        week_target_so_far = week_elapsed_workdays * hours_per_day
        week_difference = week_total_hours - week_target_so_far

    return jsonify({
        "year": year,
        "month": month,
        "hours_per_day": round(hours_per_day, 4),
        "hours_per_week": hours_per_week,
        "work_days_per_week": work_days_per_week,
        "total_hours": round(total_hours, 2),
        "target_hours": round(target_hours, 2),
        "expected_so_far": round(expected_so_far, 2),
        "difference": round(difference, 2),
        "on_track": difference >= 0,
        "total_workdays": total_workdays,
        "elapsed_workdays": elapsed_workdays,
        "week_difference": round(week_difference, 2),
        "week_total_hours": round(week_total_hours, 2),
        "week_elapsed_workdays": week_elapsed_workdays,
        "week_target_so_far": week_target_so_far,
        "current_week": current_week_key,
        "daily": dict(sorted(daily.items())),
        "weekly": week_list,
    })
