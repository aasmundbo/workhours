"""Routes for managing no-work (off) days — e.g. public holidays."""

from datetime import datetime

from flask import Blueprint, jsonify, request

from storage import add_off_day, load_off_days, remove_off_day

off_days_bp = Blueprint("off_days", __name__)


@off_days_bp.route("/api/off-days", methods=["GET"])
def get_off_days():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    off_days = load_off_days()
    if year and month:
        prefix = f"{year:04d}-{month:02d}"
        off_days = [d for d in off_days if d.startswith(prefix)]
    return jsonify(off_days)


@off_days_bp.route("/api/off-days", methods=["POST"])
def create_off_day():
    data = request.get_json()
    if not data or "date" not in data:
        return jsonify({"error": "date required"}), 400
    date = data["date"]
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    add_off_day(date)
    return jsonify({"date": date}), 201


@off_days_bp.route("/api/off-days/<date>", methods=["DELETE"])
def delete_off_day(date: str):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if not remove_off_day(date):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"date": date})
