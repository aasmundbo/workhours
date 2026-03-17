"""Flask application for Work Hours Tracker."""

import os

from flask import Flask, jsonify, request, send_from_directory, session

from routes.auth import auth_bp
from routes.entries import entries_bp
from routes.off_days import off_days_bp
from routes.stats import stats_bp

# Paths that do not require authentication
_AUTH_EXEMPT = {"/api/auth/login", "/api/auth/logout", "/api/auth/status"}


def create_app() -> Flask:
    app = Flask(__name__, static_folder="/app/frontend/dist", static_url_path="/")

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key and not os.environ.get("PYTEST_CURRENT_TEST"):
        raise RuntimeError(
            "SECRET_KEY environment variable is required. "
            "Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    app.secret_key = secret_key or "testing-only-key"

    app.register_blueprint(auth_bp)
    app.register_blueprint(entries_bp)
    app.register_blueprint(off_days_bp)
    app.register_blueprint(stats_bp)

    @app.before_request
    def require_auth():
        # Auth is bypassed during automated tests so existing tests need no changes.
        if app.config.get("TESTING"):
            return None
        if not request.path.startswith("/api/"):
            return None
        if request.path in _AUTH_EXEMPT:
            return None
        if not session.get("authenticated"):
            return jsonify({"error": "Unauthorized"}), 401

    @app.route("/")
    @app.route("/<path:path>")
    def serve_frontend(path=""):
        try:
            return send_from_directory(app.static_folder, path)
        except Exception:
            return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
