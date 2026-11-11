from pathlib import Path
import sqlite3
import sys
from urllib.parse import urlsplit

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from backend.scrape_control import BusyError, ScrapeStore, available_companies


def create_app(store=None):
    app = Flask(__name__)
    CORS(app)
    store = store if store is not None else ScrapeStore()

    @app.before_request
    def local_admin_only():
        if not request.path.startswith("/api/admin/"):
            return None
        hosts = {"localhost", "127.0.0.1", "::1"}
        origin = request.headers.get("Origin")
        try:
            trusted = (
                request.remote_addr in {"127.0.0.1", "::1"}
                and urlsplit("//" + request.host).hostname in hosts
                and (not origin or urlsplit(origin).hostname in hosts)
            )
        except ValueError:
            trusted = False
        if not trusted:
            return jsonify(error="Scraper administration is available only through localhost on this computer."), 403
        if request.method in {"POST", "PUT"} and not request.is_json:
            return jsonify(error="Send an application/json request."), 415
        return None

    @app.errorhandler(ValueError)
    def invalid_settings(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(BadRequest)
    def invalid_json(error):
        return jsonify(error="Send valid JSON."), 400

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception("Database operation failed")
        return jsonify(error="The database could not be updated. Check the backend logs."), 503

    @app.route("/api")
    def jobs():
        with store.connection() as conn:
            companies = dict(conn.execute("SELECT id, name FROM companies").fetchall())
            rows = conn.execute(
                "SELECT id, job_id, title, company_id, created_at, date_posted, link, tags, "
                "salary_min, salary_max, summary FROM jobs",
            ).fetchall()
        return jsonify([
            {
                "id": row[0], "job_id": row[1], "title": row[2],
                "company": companies.get(row[3], ""), "created_at": row[4],
                "date_posted": row[5], "link": row[6], "tags": row[7],
                "salary_min": row[8], "salary_max": row[9], "summary": row[10],
            }
            for row in rows
        ])

    @app.route("/api/admin/scraper", methods=["GET", "PUT"])
    def scraper_settings():
        if request.method == "PUT":
            settings = store.save_settings(request.get_json())
        else:
            settings, _ = store.load_settings()
        return jsonify(settings=settings, companies=available_companies(), status=store.status())

    @app.route("/api/admin/scraper/status")
    def scraper_status():
        return jsonify(store.status())

    @app.route("/api/admin/scraper/run", methods=["POST"])
    def manual_scrape():
        try:
            run_id = store.enqueue()
        except BusyError as error:
            return jsonify(error=str(error)), 409
        return jsonify(run_id=run_id, status=store.status()), 202

    return app


app = create_app()

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
