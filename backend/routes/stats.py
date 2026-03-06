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
            if datetime(year, month, d).weekday() < 5
        )
    else:
        elapsed_workdays = 0

    # Target: 40h/week ≈ 8h/workday
    target_hours = total_workdays * 8
    expected_so_far = elapsed_workdays * 8
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
    week_target_so_far = 0

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
                for i in range(5)
                if (week_start + timedelta(days=i)) <= week_cutoff
            )
        else:
            week_elapsed_workdays = 0

        week_target_so_far = week_elapsed_workdays * 8
        week_difference = week_total_hours - week_target_so_far

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
        "week_difference": round(week_difference, 2),
        "week_total_hours": round(week_total_hours, 2),
        "week_elapsed_workdays": week_elapsed_workdays,
        "week_target_so_far": week_target_so_far,
        "current_week": current_week_key,
        "daily": dict(sorted(daily.items())),
        "weekly": week_list,
    })
