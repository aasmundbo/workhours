"""Statistics and aggregation routes."""

from collections import defaultdict
from datetime import datetime, timedelta
from calendar import monthrange

from flask import Blueprint, jsonify, request

from storage import load_entries

stats_bp = Blueprint("stats", __name__)


def _get_iso_week(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _weeks_in_month(year: int, month: int) -> list[dict]:
    """Return all ISO weeks that overlap with the given month."""
    _, num_days = monthrange(year, month)
    weeks = {}
    for day in range(1, num_days + 1):
        d = datetime(year, month, day)
        iso = d.isocalendar()
        week_key = f"{iso[0]}-W{iso[1]:02d}"
        if week_key not in weeks:
            # Monday of this ISO week
            monday = d - timedelta(days=d.weekday())
            friday = monday + timedelta(days=4)
            weeks[week_key] = {
                "week": week_key,
                "start": monday.strftime("%Y-%m-%d"),
                "end": friday.strftime("%Y-%m-%d"),
                "hours": 0.0,
                "target": 40.0,
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
    weeks = _weeks_in_month(year, month)
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
        if datetime(year, month, d).weekday() < 5
    )

    today = datetime.now()
    if today.year == year and today.month == month:
        elapsed_workdays = sum(
            1
            for d in range(1, min(today.day, num_days) + 1)
            if datetime(year, month, d).weekday() < 5
        )
    else:
        elapsed_workdays = total_workdays

    # Target: 40h/week ≈ 8h/workday
    target_hours = total_workdays * 8
    expected_so_far = elapsed_workdays * 8
    difference = total_hours - expected_so_far

    return jsonify({
        "year": year,
        "month": month,
        "total_hours": round(total_hours, 2),
        "target_hours": target_hours,
        "expected_so_far": expected_so_far,
        "difference": round(difference, 2),
        "on_track": difference >= 0,
        "total_workdays": total_workdays,
        "elapsed_workdays": elapsed_workdays,
        "daily": dict(sorted(daily.items())),
        "weekly": week_list,
    })
