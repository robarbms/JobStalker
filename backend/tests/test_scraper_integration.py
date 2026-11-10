from contextlib import closing, ExitStack
import importlib
from pathlib import Path
import runpy
import sqlite3
import unittest
from unittest.mock import Mock, patch

from backend.scrapers.board_scraper import ScraperError
from backend.tests.test_new_scrapers import SCRAPERS


class ScraperIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module("backend.scrapers.getAllJobs")

    def mock_scrapers(self, stack):
        return {
            name: stack.enter_context(patch.object(self.module, name, return_value=([], 0)))
            for name in vars(self.module)
            if name.startswith("get") and name.endswith("Jobs") and name != "getAllJobs"
        }

    def test_collection_runs_every_new_scraper_and_preserves_known_ids(self):
        with ExitStack() as stack:
            scrapers = self.mock_scrapers(stack)
            stack.enter_context(patch.object(self.module, "log"))
            for company, function in SCRAPERS.values():
                scrapers[function].return_value = ([{"company": company, "job_id": "new"}], 2)
            ids = {"Reddit": ["known"]}
            jobs, count = self.module.getAllJobs(ids, ["engineer"])
        self.assertEqual(len(jobs), len(SCRAPERS))
        self.assertEqual(count, 2 * len(SCRAPERS))
        for company, function in SCRAPERS.values():
            scrapers[function].assert_called_once_with(ids.get(company, []), ["engineer"])
        self.assertEqual(ids, {"Reddit": ["known"]})

    def test_one_failed_board_does_not_stop_later_companies(self):
        with ExitStack() as stack:
            scrapers = self.mock_scrapers(stack)
            logger = stack.enter_context(patch.object(self.module, "log"))
            scrapers["getTikTokJobs"].side_effect = ScraperError("TikTok unavailable")
            scrapers["getPandoraJobs"].return_value = ([{"job_id": "last"}], 1)
            self.assertEqual(self.module.getAllJobs({}, ["engineer"]), ([{"job_id": "last"}], 1))
        logger.assert_any_call("Error fetching jobs for TikTok: TikTok unavailable", "error")
        scrapers["getPandoraJobs"].assert_called_once()

    def test_empty_query_list_does_not_index_first_query(self):
        with ExitStack() as stack:
            scrapers = self.mock_scrapers(stack)
            stack.enter_context(patch.object(self.module, "log"))
            self.assertEqual(self.module.getAllJobs({}, []), ([], 0))
        for scraper in scrapers.values():
            scraper.assert_not_called()

    def test_database_setup_registers_every_scraper_company_idempotently(self):
        path = Path(__file__).resolve().parents[1] / "database" / "createTables.py"
        with patch.dict("sys.modules", {"connection": Mock()}):
            setup = runpy.run_path(str(path))
        with closing(sqlite3.connect(":memory:")) as connection:
            cursor = connection.cursor()
            setup["createTables"](cursor, connection)
            setup["addCompanies"](cursor, connection, setup["companies"])
            setup["addCompanies"](cursor, connection, setup["companies"])
            names = {row[0] for row in cursor.execute("SELECT name FROM companies")}
            for company, _ in SCRAPERS.values():
                with self.subTest(company=company):
                    self.assertIn(company, names)
            self.assertEqual(
                cursor.execute("SELECT COUNT(*) FROM companies").fetchone()[0], len(names),
            )


if __name__ == "__main__":
    unittest.main()
