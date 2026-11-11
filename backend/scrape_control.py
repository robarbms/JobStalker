"""Persistent scraper configuration and the queue shared by the API and worker."""

from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
import json
import sqlite3
import threading
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apscheduler.triggers.cron import CronTrigger

from backend.database.connection import connect_to_db


UTC = timezone.utc
WORKER_TIMEOUT = timedelta(seconds=45)
STARTUP_DELAY = timedelta(minutes=30)
DEFAULT_KEYWORDS = [
    "engineer", "developer", "full stack", ".net", "software", "application",
    "backend", "game", "development", "c++",
]


def utcnow():
    return datetime.now(UTC)


def timestamp(value):
    return value.astimezone(UTC).isoformat()


def parse_time(value):
    return datetime.fromisoformat(value) if value else None


def available_companies():
    from backend.scrapers.company_locations import get_company_location
    from backend.scrapers.getAllJobs import get_scrapers
    return [
        {"name": name, "location": get_company_location(name)}
        for name in sorted(get_scrapers(), key=str.casefold)
    ]


def default_settings():
    return {
        "keywords": DEFAULT_KEYWORDS.copy(),
        "max_jobs": 100,
        "companies": [company["name"] for company in available_companies()],
        "schedule": {
            "enabled": False, "interval_minutes": 120, "times": [],
            "weekdays": list(range(7)), "timezone": "UTC",
        },
    }


def validate_settings(value):
    if not isinstance(value, dict) or set(value) != {"keywords", "max_jobs", "companies", "schedule"}:
        raise ValueError("Provide keywords, max_jobs, companies, and schedule.")
    keywords = value["keywords"]
    if (
        not isinstance(keywords, list) or not keywords or len(keywords) > 200
        or any(not isinstance(word, str) or not word.strip() or len(word) > 200 for word in keywords)
    ):
        raise ValueError("Enter 1 to 200 nonempty keywords, each at most 200 characters.")
    limit = value["max_jobs"]
    if type(limit) is not int or limit < 1:
        raise ValueError("max_jobs must be a positive whole number of new jobs per company.")
    names = value["companies"]
    known = {company["name"] for company in available_companies()}
    if not isinstance(names, list) or not names or any(
        not isinstance(name, str) or name not in known for name in names
    ):
        raise ValueError("Select at least one available company.")
    schedule = value["schedule"]
    if not isinstance(schedule, dict) or set(schedule) != {
        "enabled", "interval_minutes", "times", "weekdays", "timezone",
    }:
        raise ValueError("Provide all schedule fields.")
    if type(schedule["enabled"]) is not bool:
        raise ValueError("Schedule enabled must be true or false.")
    interval = schedule["interval_minutes"]
    if interval is not None and (type(interval) is not int or interval < 1):
        raise ValueError("The interval must be a positive whole number of minutes.")
    if interval is not None:
        try:
            utcnow() + timedelta(minutes=interval)
        except OverflowError as error:
            raise ValueError("The interval exceeds the supported calendar range.") from error
    days = schedule["weekdays"]
    if not isinstance(days, list) or not days or any(type(day) is not int or day not in range(7) for day in days):
        raise ValueError("Select at least one weekday (Monday is 0; Sunday is 6).")
    times = schedule["times"]
    if not isinstance(times, list) or any(
        not isinstance(value, str) or len(value) != 5
        or value[2] != ":" or not value[:2].isdigit() or not value[3:].isdigit()
        or int(value[:2]) > 23 or int(value[3:]) > 59 for value in times
    ):
        raise ValueError("Clock times must use HH:MM, from 00:00 to 23:59.")
    zone = schedule["timezone"]
    if not isinstance(zone, str) or not zone or len(zone) > 100:
        raise ValueError("Enter an IANA timezone, such as America/New_York or UTC.")
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ValueError("Unknown timezone. Use an IANA name such as America/New_York or UTC.") from error
    return {
        "keywords": list(dict.fromkeys(word.strip().casefold() for word in keywords)),
        "max_jobs": limit, "companies": sorted(set(names), key=str.casefold),
        "schedule": {
            "enabled": schedule["enabled"], "interval_minutes": interval,
            "times": sorted(set(times)), "weekdays": sorted(set(days)), "timezone": zone,
        },
    }


def next_scrape(settings, started_at, updated_at, finished_at=None):
    schedule = settings["schedule"]
    if not schedule["enabled"]:
        return None
    anchor = max(value for value in (started_at, updated_at, finished_at) if value is not None)
    zone = ZoneInfo(schedule["timezone"])
    days = ",".join(str(day) for day in schedule["weekdays"])
    candidates = []
    interval = schedule["interval_minutes"]
    if interval is not None:
        due = max(anchor + timedelta(minutes=interval), started_at + STARTUP_DELAY)
        if due.astimezone(zone).weekday() not in schedule["weekdays"]:
            due = CronTrigger(
                day_of_week=days, hour=0, minute=0, timezone=zone,
            ).get_next_fire_time(None, due).astimezone(UTC)
        candidates.append((due, "interval"))
    for clock_time in schedule["times"] or ([] if interval is not None else ["00:00"]):
        hour, minute = map(int, clock_time.split(":"))
        due = CronTrigger(
            day_of_week=days, hour=hour, minute=minute, timezone=zone,
        ).get_next_fire_time(None, anchor + timedelta(microseconds=1))
        candidates.append((due.astimezone(UTC), "clock"))
    return min(candidates, key=lambda candidate: candidate[0])


class BusyError(RuntimeError):
    pass


class ScrapeStore:
    def __init__(self, connect=connect_to_db, now=utcnow):
        self.connect = connect
        self.now = now
        self.initialized = False
        self.schema_lock = threading.Lock()

    @contextmanager
    def connection(self):
        _, conn = self.connect()
        if conn is None:
            raise RuntimeError("The application database is unavailable.")
        with closing(conn):
            conn.row_factory = sqlite3.Row
            with self.schema_lock:
                if not self.initialized:
                    conn.executescript("""
                        CREATE TABLE IF NOT EXISTS scraper_settings (
                            id INTEGER PRIMARY KEY CHECK (id = 1),
                            settings_json TEXT NOT NULL, updated_at TEXT NOT NULL
                        );
                        CREATE TABLE IF NOT EXISTS scrape_runs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL,
                            status TEXT NOT NULL, requested_at TEXT NOT NULL,
                            started_at TEXT, finished_at TEXT, worker_token TEXT,
                            settings_json TEXT NOT NULL, jobs_found INTEGER NOT NULL DEFAULT 0,
                            jobs_added INTEGER NOT NULL DEFAULT 0, errors_json TEXT NOT NULL DEFAULT '[]'
                        );
                        CREATE TABLE IF NOT EXISTS scraper_worker (
                            id INTEGER PRIMARY KEY CHECK (id = 1), token TEXT NOT NULL,
                            started_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL
                        );
                    """)
                    conn.execute(
                        "INSERT OR IGNORE INTO scraper_settings VALUES (1, ?, ?)",
                        (json.dumps(default_settings()), timestamp(self.now())),
                    )
                    conn.commit()
                    self.initialized = True
            with conn:
                yield conn

    def load_settings(self):
        with self.connection() as conn:
            row = conn.execute("SELECT settings_json, updated_at FROM scraper_settings WHERE id = 1").fetchone()
            return json.loads(row["settings_json"]), parse_time(row["updated_at"])

    def save_settings(self, value):
        settings = validate_settings(value)
        with self.connection() as conn:
            conn.execute(
                "UPDATE scraper_settings SET settings_json = ?, updated_at = ? WHERE id = 1",
                (json.dumps(settings), timestamp(self.now())),
            )
            conn.execute(
                "UPDATE scrape_runs SET status = 'cancelled', finished_at = ? "
                "WHERE status = 'queued' AND source != 'manual'", (timestamp(self.now()),),
            )
        return settings

    @staticmethod
    def run(row, include_settings=False):
        if row is None:
            return None
        result = dict(row)
        result["errors"] = json.loads(result.pop("errors_json"))
        settings = json.loads(result.pop("settings_json"))
        result.pop("worker_token")
        if include_settings:
            result["settings"] = settings
        return result

    def status(self):
        settings, updated = self.load_settings()
        with self.connection() as conn:
            worker = conn.execute("SELECT * FROM scraper_worker WHERE id = 1").fetchone()
            active = conn.execute(
                "SELECT * FROM scrape_runs WHERE status IN ('queued', 'running') ORDER BY id LIMIT 1",
            ).fetchone()
            last = conn.execute(
                "SELECT * FROM scrape_runs WHERE status NOT IN ('queued', 'running') ORDER BY id DESC LIMIT 1",
            ).fetchone()
        online = bool(worker and self.now() - parse_time(worker["heartbeat_at"]) < WORKER_TIMEOUT)
        due = next_scrape(
            settings, parse_time(worker["started_at"]), updated,
            parse_time(last["finished_at"]) if last else None,
        ) if online and active is None else None
        return {
            "worker_online": online, "worker_started_at": worker["started_at"] if worker else None,
            "next_run_at": timestamp(due[0]) if due else None,
            "active_run": self.run(active), "last_run": self.run(last),
        }

    def enqueue(self, source="manual", expected_updated=None):
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            worker = conn.execute("SELECT heartbeat_at FROM scraper_worker WHERE id = 1").fetchone()
            if not worker or self.now() - parse_time(worker["heartbeat_at"]) >= WORKER_TIMEOUT:
                raise BusyError("The scraper worker is offline. Start backend\\main.py first.")
            if conn.execute(
                "SELECT 1 FROM scrape_runs WHERE status IN ('queued', 'running')",
            ).fetchone():
                raise BusyError("A scrape is already queued or running.")
            row = conn.execute("SELECT settings_json, updated_at FROM scraper_settings WHERE id = 1").fetchone()
            if expected_updated is not None and row["updated_at"] != timestamp(expected_updated):
                raise BusyError("The schedule changed; checking it again on the next tick.")
            cursor = conn.execute(
                "INSERT INTO scrape_runs (source, status, requested_at, settings_json) VALUES (?, 'queued', ?, ?)",
                (source, timestamp(self.now()), row["settings_json"]),
            )
            return cursor.lastrowid

    def acquire_worker(self, token):
        started = self.now()
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            worker = conn.execute("SELECT * FROM scraper_worker WHERE id = 1").fetchone()
            if worker and self.now() - parse_time(worker["heartbeat_at"]) < WORKER_TIMEOUT:
                raise BusyError("Another scraper worker is already running.")
            conn.execute(
                "UPDATE scrape_runs SET status = 'failed', finished_at = ?, errors_json = ? WHERE status = 'running'",
                (timestamp(started), json.dumps(["The previous worker stopped before this scrape completed."])),
            )
            conn.execute(
                "UPDATE scrape_runs SET status = 'cancelled', finished_at = ? "
                "WHERE status = 'queued' AND source != 'manual'",
                (timestamp(started),),
            )
            conn.execute(
                "INSERT OR REPLACE INTO scraper_worker VALUES (1, ?, ?, ?)",
                (token, timestamp(started), timestamp(started)),
            )
        return started

    def heartbeat(self, token):
        with self.connection() as conn:
            if conn.execute(
                "UPDATE scraper_worker SET heartbeat_at = ? WHERE token = ?",
                (timestamp(self.now()), token),
            ).rowcount != 1:
                raise RuntimeError("This worker no longer owns the scraper lease.")

    def claim(self, token):
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            worker = conn.execute("SELECT * FROM scraper_worker WHERE token = ?", (token,)).fetchone()
            if worker is None:
                raise RuntimeError("This worker no longer owns the scraper lease.")
            if conn.execute("SELECT 1 FROM scrape_runs WHERE status = 'running'").fetchone():
                return None
            row = conn.execute("SELECT * FROM scrape_runs WHERE status = 'queued' ORDER BY id LIMIT 1").fetchone()
            if row is None:
                return None
            settings = json.loads(row["settings_json"])
            schedule = settings["schedule"]
            if row["source"] != "manual" and self.now().astimezone(ZoneInfo(schedule["timezone"])).weekday() not in schedule["weekdays"]:
                conn.execute(
                    "UPDATE scrape_runs SET status = 'cancelled', finished_at = ? WHERE id = ?",
                    (timestamp(self.now()), row["id"]),
                )
                return None
            if row["source"] == "interval" and self.now() < parse_time(worker["started_at"]) + STARTUP_DELAY:
                return None
            conn.execute(
                "UPDATE scrape_runs SET status = 'running', started_at = ?, worker_token = ? WHERE id = ?",
                (timestamp(self.now()), token, row["id"]),
            )
            return self.run(conn.execute("SELECT * FROM scrape_runs WHERE id = ?", (row["id"],)).fetchone(), True)

    def progress(self, run_id, token, found, added, errors):
        with self.connection() as conn:
            if conn.execute(
                "UPDATE scrape_runs SET jobs_found = ?, jobs_added = ?, errors_json = ? "
                "WHERE id = ? AND worker_token = ? AND status = 'running'",
                (found, added, json.dumps(errors), run_id, token),
            ).rowcount != 1:
                raise RuntimeError("This worker no longer owns the scrape.")

    def finish(self, run_id, token, error=None):
        with self.connection() as conn:
            row = conn.execute("SELECT errors_json FROM scrape_runs WHERE id = ?", (run_id,)).fetchone()
            errors = json.loads(row["errors_json"])
            if error:
                errors.append(error)
            status = "failed" if error else "completed_with_errors" if errors else "completed"
            result = conn.execute(
                "UPDATE scrape_runs SET status = ?, finished_at = ?, errors_json = ? "
                "WHERE id = ? AND worker_token = ? AND status = 'running'",
                (status, timestamp(self.now()), json.dumps(errors), run_id, token),
            )
            if result.rowcount != 1:
                raise RuntimeError("This worker no longer owns the scrape.")

    def release_worker(self, token):
        with self.connection() as conn:
            conn.execute(
                "UPDATE scrape_runs SET status = 'failed', finished_at = ?, errors_json = ? "
                "WHERE status = 'running' AND worker_token = ?",
                (timestamp(self.now()), json.dumps(["The worker stopped during this scrape."]), token),
            )
            conn.execute("DELETE FROM scraper_worker WHERE token = ?", (token,))
