"""Authentication routes (single-user password login)."""

import os

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    password_hash = os.environ.get("APP_PASSWORD_HASH", "")
    if not password_hash:
        return jsonify({"error": "Server not configured: APP_PASSWORD_HASH not set"}), 500
    if not check_password_hash(password_hash, password):
        return jsonify({"error": "Invalid password"}), 401
    session.clear()
    session["authenticated"] = True
    return jsonify({"authenticated": True})


@auth_bp.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@auth_bp.get("/api/auth/status")
def status():
    if os.environ.get("DISABLE_AUTH") == "true":
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": bool(session.get("authenticated"))})
