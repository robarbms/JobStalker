from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
import runpy
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

from backend.api.app import create_app
from backend.scrape_control import BusyError, ScrapeStore, UTC, next_scrape
from backend.scrape_worker import ScrapeWorker, execute_scrape
from backend.scrapers.board_scraper import record
from backend.scrapers.scraper_utils import get_queries


class ScrapeControlTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "jobs.db"
        self.now = datetime(2026, 11, 9, 8, tzinfo=UTC)
        self.store = ScrapeStore(self.connect, lambda: self.now)
        self.settings, _ = self.store.load_settings()
        self.settings["companies"] = ["Reddit"]
        self.store.save_settings(self.settings)
        self.client = create_app(self.store).test_client()

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=30)
        return conn.cursor(), conn

    def worker(self, execute=None):
        execute = execute or Mock(side_effect=lambda settings, progress: progress(4, 2, []))
        worker = ScrapeWorker(self.store, execute)
        worker.start()
        self.addCleanup(self.store.release_worker, worker.token)
        return worker, execute

    def schedule(self, interval=5, times=None, days=None, zone="UTC"):
        self.settings["schedule"] = {
            "enabled": True, "interval_minutes": interval, "times": times or [],
            "weekdays": list(range(7)) if days is None else days, "timezone": zone,
        }
        self.store.save_settings(self.settings)

    def test_keywords_are_persistent_and_do_not_read_config_ini(self):
        self.settings.update(keywords=[" Rust ", "RUST", "platform"], max_jobs=3)
        response = self.client.put("/api/admin/scraper", json=self.settings)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["settings"]["keywords"], ["rust", "platform"])
        reopened = ScrapeStore(self.connect, lambda: self.now)
        with patch("backend.scrape_control.ScrapeStore", return_value=reopened):
            self.assertEqual(get_queries(), ["rust", "platform"])
        self.assertEqual(reopened.load_settings()[0]["max_jobs"], 3)

    def test_invalid_settings_do_not_replace_saved_settings(self):
        invalid = [
            {"max_jobs": 0}, {"max_jobs": True}, {"max_jobs": 1.5},
            {"keywords": []}, {"companies": []}, {"companies": ["Unknown"]},
        ]
        schedule_invalid = [
            {"interval_minutes": 0}, {"interval_minutes": 1.5}, {"weekdays": []},
            {"interval_minutes": 10 ** 100},
            {"weekdays": [True]}, {"times": ["24:00"]}, {"times": ["9:30"]},
            {"timezone": "Not/A_Timezone"}, {"enabled": "yes"},
        ]
        for change in invalid:
            with self.subTest(change=change):
                settings = {**deepcopy(self.settings), **change}
                self.assertEqual(self.client.put("/api/admin/scraper", json=settings).status_code, 400)
        for change in schedule_invalid:
            with self.subTest(schedule=change):
                settings = deepcopy(self.settings)
                settings["schedule"].update(change)
                self.assertEqual(self.client.put("/api/admin/scraper", json=settings).status_code, 400)
        self.assertEqual(self.store.load_settings()[0], self.settings)

    def test_admin_is_local_only_and_rejects_cross_origin_or_form_posts(self):
        for options in (
            {"environ_overrides": {"REMOTE_ADDR": "192.168.1.10"}},
            {"headers": {"Origin": "https://untrusted.example"}},
            {"headers": {"Host": "untrusted.example"}},
        ):
            with self.subTest(options=options):
                self.assertEqual(self.client.get("/api/admin/scraper", **options).status_code, 403)
                self.assertEqual(self.client.post("/api/admin/scraper/run", json={}, **options).status_code, 403)
        self.assertEqual(self.client.post("/api/admin/scraper/run", data={}).status_code, 415)
        self.assertEqual(self.client.put(
            "/api/admin/scraper", data="{", content_type="application/json",
        ).status_code, 400)
        response = self.client.get("/api/admin/scraper", headers={"Origin": "http://localhost:3000"})
        self.assertEqual(response.status_code, 200)

    def test_offline_worker_is_reported_and_cannot_accept_a_manual_run(self):
        self.assertFalse(self.client.get("/api/admin/scraper/status").json["worker_online"])
        response = self.client.post("/api/admin/scraper/run", json={})
        self.assertEqual(response.status_code, 409)
        self.assertIn("offline", response.json["error"])

    def test_manual_run_is_immediate_uses_a_snapshot_and_reports_progress(self):
        worker, execute = self.worker()
        self.schedule(days=[6])
        response = self.client.post("/api/admin/scraper/run", json={})
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json["status"]["active_run"]["status"], "queued")
        self.assertEqual(self.client.post("/api/admin/scraper/run", json={}).status_code, 409)
        self.settings["keywords"] = ["replacement"]
        self.store.save_settings(self.settings)
        worker.tick()
        self.assertEqual(execute.call_count, 1)
        self.assertNotEqual(execute.call_args.args[0]["keywords"], ["replacement"])
        status = self.store.status()
        self.assertIsNone(status["active_run"])
        self.assertEqual(status["last_run"]["status"], "completed")
        self.assertEqual(status["last_run"]["jobs_added"], 2)

    def test_interval_waits_thirty_minutes_then_allows_five_minute_intervals(self):
        self.schedule()
        worker, execute = self.worker()
        worker.tick()
        self.now += timedelta(minutes=29, seconds=59)
        worker.tick()
        execute.assert_not_called()
        self.now += timedelta(seconds=1)
        worker.tick()
        self.assertEqual(execute.call_count, 1)
        self.now += timedelta(minutes=4, seconds=59)
        worker.tick()
        self.assertEqual(execute.call_count, 1)
        self.now += timedelta(seconds=1)
        worker.tick()
        self.assertEqual(execute.call_count, 2)

    def test_long_interval_waits_its_full_duration_at_startup(self):
        self.schedule(interval=120)
        worker, execute = self.worker()
        self.now += timedelta(minutes=119)
        worker.tick()
        execute.assert_not_called()
        self.now += timedelta(minutes=1)
        worker.tick()
        execute.assert_called_once()

    def test_clock_times_can_run_before_the_interval_startup_delay(self):
        self.schedule(times=["08:10"])
        worker, execute = self.worker()
        self.now += timedelta(minutes=10)
        worker.tick()
        self.assertEqual(self.store.status()["last_run"]["source"], "clock")
        self.now += timedelta(minutes=19)
        worker.tick()
        self.assertEqual(execute.call_count, 1)
        self.now += timedelta(minutes=1)
        worker.tick()
        self.assertEqual(execute.call_count, 2)
        self.assertEqual(self.store.status()["last_run"]["source"], "interval")

    def test_weekdays_restrict_both_interval_and_clock_times(self):
        self.schedule(times=["08:10"], days=[1])
        worker, execute = self.worker()
        self.now += timedelta(hours=12)
        worker.tick()
        execute.assert_not_called()
        self.assertEqual(self.store.status()["next_run_at"], "2026-11-10T00:00:00+00:00")

    def test_days_only_schedule_runs_at_midnight_in_its_timezone(self):
        self.schedule(interval=None, days=[2], zone="America/Los_Angeles")
        due, source = next_scrape(self.settings, self.now, self.now)
        self.assertEqual((due, source), (datetime(2026, 11, 11, 8, tzinfo=UTC), "clock"))

    def test_disabling_schedule_and_changing_company_selection_affect_future_runs(self):
        self.schedule()
        worker, execute = self.worker()
        self.now += timedelta(minutes=20)
        self.settings["schedule"]["enabled"] = False
        self.settings["companies"] = ["Buffer"]
        self.store.save_settings(self.settings)
        self.now += timedelta(hours=1)
        worker.tick()
        execute.assert_not_called()
        self.assertIsNone(self.store.status()["next_run_at"])
        self.store.enqueue()
        worker.tick()
        self.assertEqual(execute.call_args.args[0]["companies"], ["Buffer"])

    def test_concurrent_manual_requests_queue_only_one_run(self):
        self.worker()

        def enqueue(_):
            try:
                return self.store.enqueue()
            except BusyError:
                return None

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(enqueue, range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)

    def test_duplicate_worker_is_rejected_and_crashed_worker_is_recovered(self):
        self.worker()
        with self.assertRaises(BusyError):
            self.worker()
        run_id = self.store.enqueue()
        with self.store.connection() as conn:
            conn.execute("UPDATE scrape_runs SET status = 'running' WHERE id = ?", (run_id,))
        self.now += timedelta(minutes=1)
        self.worker()
        self.assertEqual(self.store.status()["last_run"]["status"], "failed")

    def test_worker_failures_and_partial_board_errors_are_visible(self):
        worker, execute = self.worker()
        execute.side_effect = lambda settings, progress: progress(4, 2, ["Rapid7: blocked"])
        self.store.enqueue()
        worker.tick()
        self.assertEqual(self.store.status()["last_run"]["status"], "completed_with_errors")
        execute.side_effect = RuntimeError("Processing failed")
        self.store.enqueue()
        with self.assertLogs("backend.scrape_worker", level="ERROR"):
            worker.tick()
        self.assertEqual(self.store.status()["last_run"]["status"], "failed")
        self.assertEqual(self.store.status()["last_run"]["errors"], ["Processing failed"])

    def test_pipeline_persists_only_new_jobs_up_to_the_company_limit(self):
        with patch.dict("sys.modules", {"connection": Mock()}):
            setup = runpy.run_path(str(Path(__file__).resolve().parents[1] / "database" / "createTables.py"))
        cur, conn = self.connect()
        try:
            setup["createTables"](cur, conn)
            setup["addCompanies"](cur, conn, [
                {"name": "Reddit", "address": "", "site_url": "", "stock": ""},
            ])
        finally:
            conn.close()
        self.settings.update(keywords=["engineer"], max_jobs=2)
        jobs = [
            {**record(str(index), "Software Engineer", f"https://example.com/{index}", "Build services.", "Remote"),
             "company": "Reddit"} for index in range(4)
        ]
        processor = Mock(side_effect=lambda jobs: [{**job, "tags": "[]"} for job in jobs])
        progress = Mock()
        with patch("backend.database.connect_to_db", side_effect=self.connect), \
                patch("backend.scrapers.getAllJobs.getRedditJobs", return_value=(jobs, 4)), \
                patch("backend.scrapers.getAllJobs.log"), \
                patch("backend.processing.processJobs", processor), \
                patch.dict("sys.modules", {"backend.ai": Mock(get_summary=Mock(return_value="Summary"))}):
            execute_scrape(self.settings, progress)
            execute_scrape(self.settings, progress)
        cur, conn = self.connect()
        try:
            self.assertEqual(cur.execute("SELECT COUNT(*) FROM jobs").fetchone()[0], 4)
            self.assertEqual(cur.execute("SELECT COUNT(*) FROM jobs WHERE summary = 'Summary'").fetchone()[0], 4)
        finally:
            conn.close()
        self.assertEqual([len(call.args[0]) for call in processor.call_args_list], [2, 2])


if __name__ == "__main__":
    unittest.main()
