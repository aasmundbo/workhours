"""CRUD routes for time entries."""

from flask import Blueprint, jsonify, request

from models import create_entry, compute_hours
from storage import add_entry, delete_entry, load_entries, update_entry

entries_bp = Blueprint("entries", __name__)


@entries_bp.route("/api/entries", methods=["GET"])
def get_entries():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    entries = load_entries()

    if year and month:
        entries = [
            e
            for e in entries
            if e["date"].startswith(f"{year:04d}-{month:02d}")
        ]

    entries.sort(key=lambda e: (e["date"], e["clock_in"]))
    return jsonify(entries)


@entries_bp.route("/api/entries", methods=["POST"])
def create():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        entry = create_entry(
            date=data["date"],
            clock_in=data["clock_in"],
            clock_out=data["clock_out"],
            note=data.get("note", ""),
        )
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400

    add_entry(entry)
    return jsonify(entry), 201


@entries_bp.route("/api/entries/<entry_id>", methods=["PUT"])
def update(entry_id: str):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Recompute hours if times changed
    if "clock_in" in data and "clock_out" in data:
        try:
            data["hours"] = compute_hours(data["clock_in"], data["clock_out"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    result = update_entry(entry_id, data)
    if result is None:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify(result)


@entries_bp.route("/api/entries/<entry_id>", methods=["DELETE"])
def delete(entry_id: str):
    if delete_entry(entry_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Entry not found"}), 404
