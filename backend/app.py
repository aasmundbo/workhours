"""Flask application for Work Hours Tracker."""

from flask import Flask, send_from_directory

from routes.entries import entries_bp
from routes.off_days import off_days_bp
from routes.stats import stats_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="/app/frontend/dist", static_url_path="/")

    app.register_blueprint(entries_bp)
    app.register_blueprint(off_days_bp)
    app.register_blueprint(stats_bp)

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
