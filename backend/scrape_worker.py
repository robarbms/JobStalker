import logging
import threading
import uuid

from backend.scrape_control import BusyError, ScrapeStore, next_scrape, parse_time


logger = logging.getLogger(__name__)


def execute_scrape(settings, progress):
    from backend.database import connect_to_db, get_job_ids, insert_jobs
    from backend.processing import processJobs
    from backend.scrapers.getAllJobs import getAllJobs

    cur, conn = connect_to_db()
    if conn is None:
        raise RuntimeError("The application database is unavailable.")
    found = added = 0
    errors = []
    try:
        ids = get_job_ids(cur, conn)
        for company in settings["companies"]:
            jobs, count = getAllJobs(
                ids, settings["keywords"], companies=[company],
                max_jobs=settings["max_jobs"], errors=errors,
            )
            found += count
            if jobs:
                from backend.ai import get_summary
                processed = processJobs(jobs)
                for job in processed:
                    job["summary"] = get_summary(job["description"])
                added += insert_jobs(processed, cur, conn)
            progress(found, added, errors)
    finally:
        conn.close()


class ScrapeWorker:
    def __init__(self, store, execute=execute_scrape):
        self.store = store
        self.execute = execute
        self.token = str(uuid.uuid4())
        self.started_at = None

    def start(self):
        self.started_at = self.store.acquire_worker(self.token)

    def tick(self):
        self.store.heartbeat(self.token)
        status = self.store.status()
        if status["active_run"] is None:
            settings, updated = self.store.load_settings()
            last = status["last_run"]
            due = next_scrape(
                settings, self.started_at, updated,
                parse_time(last["finished_at"]) if last else None,
            )
            if due and due[0] <= self.store.now():
                try:
                    self.store.enqueue(due[1], expected_updated=updated)
                except BusyError as error:
                    logger.info("%s", error)
        run = self.store.claim(self.token)
        if run is None:
            return
        try:
            self.execute(
                run["settings"],
                lambda found, added, errors: self.store.progress(run["id"], self.token, found, added, errors),
            )
        except Exception as error:
            logger.exception("Scrape %s failed", run["id"])
            self.store.finish(run["id"], self.token, str(error))
        else:
            self.store.finish(run["id"], self.token)


def run_forever():
    logging.basicConfig(level=logging.INFO)
    store = ScrapeStore()
    worker = ScrapeWorker(store)
    worker.start()
    stopped = threading.Event()

    def heartbeat():
        try:
            while not stopped.wait(10):
                store.heartbeat(worker.token)
        except Exception:
            logger.exception("The scraper heartbeat failed; stopping this worker.")
            stopped.set()

    thread = threading.Thread(target=heartbeat, name="scraper-heartbeat", daemon=True)
    thread.start()
    try:
        while not stopped.is_set():
            worker.tick()
            stopped.wait(2)
    except KeyboardInterrupt:
        logger.info("Stopping the scraper worker.")
    finally:
        stopped.set()
        thread.join()
        store.release_worker(worker.token)
