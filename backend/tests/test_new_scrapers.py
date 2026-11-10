import importlib
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

from backend.scrapers import board_scraper as boards


SCRAPERS = {
    "tiktok": ("TikTok", "getTikTokJobs"),
    "reddit": ("Reddit", "getRedditJobs"),
    "smartsheet": ("Smartsheet", "getSmartsheetJobs"),
    "github": ("GitHub", "getGitHubJobs"),
    "linkedin": ("LinkedIn", "getLinkedInJobs"),
    "uber": ("Uber", "getUberJobs"),
    "doordash": ("DoorDash", "getDoorDashJobs"),
    "oracle": ("Oracle", "getOracleJobs"),
    "serpapi": ("SerpAPI", "getSerpAPIJobs"),
    "duckduckgo": ("DuckDuckGo", "getDuckDuckGoJobs"),
    "mozilla": ("Mozilla", "getMozillaJobs"),
    "square": ("Square", "getSquareJobs"),
    "shopify": ("Shopify", "getShopifyJobs"),
    "gitlab": ("GitLab", "getGitLabJobs"),
    "redfin": ("Redfin", "getRedfinJobs"),
    "hulu": ("Hulu", "getHuluJobs"),
    "zapier": ("Zapier", "getZapierJobs"),
    "spotify": ("Spotify", "getSpotifyJobs"),
    "pandora": ("Pandora", "getPandoraJobs"),
}


def response(data=None, html=""):
    result = Mock(text=html)
    result.json.return_value = data
    return result


def greenhouse(job_id, title="Software Engineer", brand="Square"):
    return {
        "id": job_id, "title": title,
        "absolute_url": f"https://example.com/jobs/{job_id}",
        "content": "&lt;p&gt;Build &amp; maintain services.&lt;/p&gt;",
        "location": {"name": "Seattle, WA"},
        "first_published": "2026-10-25T10:00:00Z",
        "updated_at": "2026-11-09T10:00:00Z",
        "metadata": [{"name": "Brands", "value": brand}],
    }


def ashby(job_id, listed=True):
    return {
        "id": job_id, "title": "Software Engineer", "jobUrl": f"https://example.com/{job_id}",
        "descriptionHtml": "<p>Build services.</p>", "location": "Remote",
        "secondaryLocations": [{"location": "Canada"}],
        "publishedAt": "2026-10-25T10:00:00Z", "isListed": listed,
    }


def lever(job_id):
    return {
        "id": job_id, "text": "Software Engineer", "hostedUrl": f"https://example.com/{job_id}",
        "description": "<p>Build services.</p>",
        "lists": [{"text": "Requirements", "content": "<ul><li>Python</li></ul>"}],
        "additional": "<p>Salary and benefits.</p>", "createdAt": 1792886400000,
        "categories": {"location": "New York, NY"},
    }


def jibe(job_id, description="<p>Build services for Pandora.</p>"):
    return {"data": {
        "req_id": job_id, "slug": str(job_id), "title": "Software Engineer",
        "description": description, "full_location": "Oakland, CA",
        "posted_date": "2026-10-25T10:00:00+0000",
    }}


def oracle_listing(job_id):
    return {
        "Id": job_id, "Title": "Software Engineer", "PrimaryLocation": "Seattle, WA",
        "PostedDate": "2026-10-25",
    }


def oracle_page(postings, total):
    return response({"items": [{"requisitionList": postings, "TotalJobsCount": total}]})


def tiktok(job_id):
    return {
        "id": job_id, "title": "Software Engineer", "description": "Build services.",
        "requirement": "Experience with Python.",
        "city_info": {"en_name": "Seattle", "parent": {"en_name": "United States", "parent": None}},
    }


def tiktok_page(postings, total):
    return response({"code": 0, "data": {"job_post_list": postings, "count": total}})


def linkedin_card(job_id):
    return f"""
        <li><div data-entity-urn="urn:li:jobPosting:{job_id}">
        <h3 class="base-search-card__title">Software Engineer</h3>
        <span class="job-search-card__location">Sunnyvale, CA</span>
        <time datetime="2026-10-25"></time></div></li>
    """


def hulu_card(job_id):
    return f"""
        <a data-job-id="{job_id}" href="/en/job/seattle/engineer/391/{job_id}">
        <h2>Software Engineer</h2><span class="job-location">Seattle, Washington</span>
        <span class="job-date-posted">Oct. 25, 2026</span></a>
    """


class NewScraperTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock(headers={})
        context = MagicMock()
        context.__enter__.return_value = self.session
        self.session_patch = patch.object(boards.requests, "Session", return_value=context)
        self.session_factory = self.session_patch.start()
        self.addCleanup(self.session_patch.stop)
        self.log_patch = patch.object(boards, "log")
        self.log_patch.start()
        self.addCleanup(self.log_patch.stop)

    def scrape(self, module, ids=None, queries=None):
        _, function = SCRAPERS[module]
        scraper = getattr(importlib.import_module(f"backend.scrapers.{module}"), function)
        return scraper([] if ids is None else ids, ["engineer"] if queries is None else queries)

    def assert_job(self, job, company, job_id):
        self.assertEqual(job["company"], company)
        self.assertEqual(job["job_id"], str(job_id))
        self.assertEqual(job["title"], "Software Engineer")
        self.assertTrue(job["description"])
        self.assertNotIn("<p>", job["description"])
        self.assertTrue(job["link"].startswith("https://"))
        for field in ("location", "date_posted", "salary_min", "salary_max", "notes", "summary"):
            self.assertIn(field, job)

    def test_all_greenhouse_employers_parse_filter_and_deduplicate(self):
        for module in ("reddit", "smartsheet", "doordash", "mozilla", "gitlab", "square"):
            with self.subTest(scraper=module):
                self.session.get.return_value = response({"jobs": [
                    greenhouse(1), greenhouse(2), greenhouse(2), greenhouse(3, "Accountant"),
                    greenhouse(4, brand="Cash App"),
                ]})
                ids = [1]
                jobs, count = self.scrape(module, ids, [" ENGINEER ", "software"])
                expected_ids = ["2"] if module == "square" else ["2", "4"]
                self.assertEqual([job["job_id"] for job in jobs], expected_ids)
                self.assertEqual(count, len(expected_ids) + 1)
                self.assertEqual(ids, [1])
                self.assert_job(jobs[0], SCRAPERS[module][0], 2)
                self.assertEqual(jobs[0]["description"], "Build & maintain services.")
                self.assertEqual(jobs[0]["date_posted"], "2026-10-25")
                self.assertEqual(self.session.get.call_args.kwargs["params"], {"content": "true"})

    def test_ashby_employers_exclude_unlisted_jobs(self):
        for module in ("duckduckgo", "zapier"):
            with self.subTest(scraper=module):
                self.session.get.return_value = response({"jobs": [
                    ashby("known"), ashby("new"), ashby("new"), ashby("private", listed=False),
                ]})
                jobs, count = self.scrape(module, ["known"])
                self.assertEqual(count, 2)
                self.assertEqual(len(jobs), 1)
                self.assert_job(jobs[0], SCRAPERS[module][0], "new")
                self.assertEqual(jobs[0]["location"], "Remote; Canada")

    def test_spotify_includes_requirements_and_benefits(self):
        self.session.get.return_value = response([lever("known"), lever("new")])
        jobs, count = self.scrape("spotify", ["known"])
        self.assertEqual(count, 2)
        self.assert_job(jobs[0], "Spotify", "new")
        self.assertIn("Python", jobs[0]["description"])
        self.assertIn("Salary and benefits.", jobs[0]["description"])
        self.assertEqual(jobs[0]["date_posted"], "2026-10-25")

    def test_spotify_paginates_full_pages(self):
        self.session.get.side_effect = [
            response([lever(str(index)) for index in range(100)]),
            response([lever("last")]),
        ]
        jobs, count = self.scrape("spotify")
        self.assertEqual((len(jobs), count), (101, 101))
        self.assertEqual(self.session.get.call_args.kwargs["params"]["skip"], 100)

    def test_github_paginates_and_skips_known_ids(self):
        self.session.get.side_effect = [
            response({"jobs": [jibe("1")], "totalCount": 2}),
            response({"jobs": [jibe("2")], "totalCount": 2}),
        ]
        jobs, count = self.scrape("github", [1])
        self.assertEqual(count, 2)
        self.assert_job(jobs[0], "GitHub", 2)
        self.assertEqual(jobs[0]["link"], "https://www.github.careers/jobs/2")
        self.assertEqual(self.session.get.call_args.kwargs["params"]["page"], 2)

    def test_pandora_does_not_match_parent_company_boilerplate(self):
        boilerplate = (
            "<p>SiriusXM and its brands (Pandora, SiriusXM Media) are leading audio entertainment.</p>"
            "<p><b>SiriusXM</b> is the leading audio entertainment company. "
            "Pandora, a subsidiary of SiriusXM, is an audio service.</p>"
        )
        self.session.get.return_value = response({"jobs": [
            jibe("unrelated", boilerplate + "<p>Maintain satellite hardware.</p>"),
            jibe("pandora", boilerplate + "<p>Develop Pandora recommendations.</p>"),
        ], "totalCount": 2})
        jobs, count = self.scrape("pandora")
        self.assertEqual(count, 1)
        self.assertEqual(len(jobs), 1)
        self.assert_job(jobs[0], "Pandora", "pandora")

    def test_oracle_and_uber_fetch_full_details_once_across_queries(self):
        for module in ("oracle", "uber"):
            with self.subTest(scraper=module):
                self.session.get.side_effect = [
                    oracle_page([oracle_listing("1")], 2),
                    oracle_page([oracle_listing("2")], 2),
                    response({"items": [{
                        "ExternalDescriptionStr": "<p>Build services.</p>",
                        "ExternalResponsibilitiesStr": "<p>Operate services.</p>",
                        "ExternalQualificationsStr": "<p>Know Python.</p>",
                    }]}),
                    oracle_page([oracle_listing("2")], 1),
                ]
                jobs, count = self.scrape(module, [1], ["full stack", "engineer"])
                self.assertEqual((len(jobs), count), (1, 2))
                self.assert_job(jobs[0], SCRAPERS[module][0], 2)
                self.assertIn("Know Python.", jobs[0]["description"])
                calls = self.session.get.call_args_list[-4:]
                self.assertIn("keyword=full stack", calls[0].kwargs["params"]["finder"])
                self.assertIn("offset=1", calls[1].kwargs["params"]["finder"])
                self.assertTrue(calls[2].args[0].endswith("recruitingCEJobRequisitionDetails"))

    def test_redfin_filters_parent_company_and_fetches_details(self):
        first = response({"facets": [{
            "facetParameter": "hiringCompany",
            "values": [
                {"descriptor": "Rocket Mortgage", "id": "rocket"},
                {"descriptor": "Redfin Corporation", "id": "redfin"},
            ],
        }]})
        posting = {
            "title": "Software Engineer", "externalPath": "/job/Seattle/Engineer_R-2",
            "bulletFields": ["R-2"], "locationsText": "Seattle, WA",
        }
        self.session.post.side_effect = [
            first, response({"jobPostings": [posting], "total": 2}),
            response({"jobPostings": [{**posting, "bulletFields": ["R-3"],
                                      "externalPath": "/job/Seattle/Engineer_R-3"}], "total": 2}),
        ]
        self.session.get.return_value = response({"jobPostingInfo": {
            "jobDescription": "<p>Build services.</p>", "startDate": "2026-10-25",
        }})
        jobs, count = self.scrape("redfin", ["R-3"])
        self.assertEqual((len(jobs), count), (1, 2))
        self.assert_job(jobs[0], "Redfin", "R-2")
        self.assertEqual(self.session.get.call_count, 1)
        self.assertEqual(self.session.post.call_args.kwargs["json"]["appliedFacets"],
                         {"hiringCompany": ["redfin"]})
        self.assertEqual(self.session.post.call_args.kwargs["json"]["offset"], 1)

    def test_tiktok_paginates_and_includes_qualifications_and_location(self):
        self.session.post.side_effect = [
            tiktok_page([tiktok("1")], 2), tiktok_page([tiktok("2")], 2),
            tiktok_page([tiktok("2")], 1),
        ]
        jobs, count = self.scrape("tiktok", [1], ["software", "engineer"])
        self.assertEqual((len(jobs), count), (1, 2))
        self.assert_job(jobs[0], "TikTok", 2)
        self.assertIn("Experience with Python.", jobs[0]["description"])
        self.assertEqual(jobs[0]["location"], "Seattle, United States")
        self.assertIsNone(jobs[0]["date_posted"])
        self.assertEqual(self.session.post.call_args_list[1].kwargs["json"]["offset"], 1)
        self.assertEqual(self.session.post.call_args.kwargs["headers"]["website-path"], "tiktok")

    def test_linkedin_uses_employer_filter_and_paginates_until_empty(self):
        self.session.get.side_effect = [
            response(html=linkedin_card(1)),
            response(html=linkedin_card(2)),
            response(html='<div class="show-more-less-html__markup">Salary disclaimer only.</div>'
                     '<div class="description__text"><div class="show-more-less-html__markup">'
                     '<p>Build services.</p></div></div>'),
            response(html=""),
        ]
        jobs, count = self.scrape("linkedin", [1])
        self.assertEqual((len(jobs), count), (1, 2))
        self.assert_job(jobs[0], "LinkedIn", 2)
        self.assertNotIn("Salary disclaimer", jobs[0]["description"])
        self.assertEqual(jobs[0]["date_posted"], "2026-10-25")
        calls = self.session.get.call_args_list
        self.assertEqual(calls[0].kwargs["params"]["f_C"], "1337")
        self.assertEqual(calls[1].kwargs["params"]["start"], 1)
        self.assertEqual(calls[2].args[0], "https://www.linkedin.com/jobs/view/2")
        self.assertEqual(calls[3].kwargs["params"]["start"], 2)

    def test_serpapi_and_shopify_parse_full_html_descriptions(self):
        for module, job_id, link, description, location in (
            ("serpapi", "software-engineer", "https://serpapi.com/careers/software-engineer",
             '<section class="about-career"><p>Build services.</p><ul><li>Python</li></ul></section>',
             '<ul class="summary"><li>Remote-first</li></ul>'),
            ("shopify", "12345678-1234-1234-1234-123456789abc",
             "https://www.shopify.com/careers/software-engineer_12345678-1234-1234-1234-123456789abc",
             '<article><section><div class="richtext"><p>Build services.</p><p>Python</p></div>'
             '</section></article>', '<article><header><p>Remote - Americas</p></header></article>'),
        ):
            with self.subTest(scraper=module):
                self.session.get.side_effect = [
                    response(html=f'<a href="{link}">Software Engineer</a>'
                             f'<a href="{link}?tracking=1">Software Engineer</a>'
                             '<a href="/about">About</a>'),
                    response(html='<h1>Software Engineer</h1>' + description + location
                             + '<script type="application/ld+json">'
                             + json.dumps({"@graph": [{"@type": "JobPosting", "datePosted": "2026-10-25"}]})
                             + '</script>'),
                ]
                jobs, count = self.scrape(module)
                self.assertEqual((len(jobs), count), (1, 1))
                self.assert_job(jobs[0], SCRAPERS[module][0], job_id)
                self.assertIn("Python", jobs[0]["description"])
                self.assertTrue(jobs[0]["location"].startswith("Remote"))
                self.assertEqual(jobs[0]["date_posted"], "2026-10-25")

    def test_website_skips_known_details(self):
        self.session.get.return_value = response(
            html='<a href="/careers/software-engineer">Software Engineer</a>',
        )
        self.assertEqual(self.scrape("serpapi", ["software-engineer"]), ([], 1))
        self.assertEqual(self.session.get.call_count, 1)

    def test_hulu_parses_dates_and_follows_pagination(self):
        self.session.get.side_effect = [
            response(html='<ul id="search-results-jobs">' + hulu_card(1) + '</ul>'
                     '<nav class="pagination"><a class="next" href="?p=2">Next</a></nav>'),
            response(html='<ul id="search-results-jobs">' + hulu_card(2) + '</ul>'),
            response(html='<div class="ats-description"><p>Build streaming services.</p></div>'),
        ]
        jobs, count = self.scrape("hulu", [1])
        self.assertEqual((len(jobs), count), (1, 2))
        self.assert_job(jobs[0], "Hulu", 2)
        self.assertEqual(jobs[0]["date_posted"], "2026-10-25")
        self.assertEqual(jobs[0]["location"], "Seattle, Washington")
        self.assertTrue(self.session.get.call_args_list[1].args[0].endswith("?p=2"))

    def test_all_new_scrapers_accept_empty_queries_without_network(self):
        for module in SCRAPERS:
            with self.subTest(scraper=module):
                self.assertEqual(self.scrape(module, queries=[]), ([], 0))
        self.session_factory.assert_not_called()

    def test_all_new_scrapers_load_default_queries(self):
        with patch.object(boards, "get_queries", return_value=[]) as defaults:
            for module, (_, name) in SCRAPERS.items():
                with self.subTest(scraper=module):
                    scraper = getattr(importlib.import_module(f"backend.scrapers.{module}"), name)
                    self.assertEqual(scraper([]), ([], 0))
            self.assertEqual(defaults.call_count, len(SCRAPERS))

    def test_http_failures_are_explicit_for_every_new_scraper(self):
        self.session.get.side_effect = requests.HTTPError("503 Service Unavailable")
        self.session.post.side_effect = requests.HTTPError("503 Service Unavailable")
        for module, (company, _) in SCRAPERS.items():
            with self.subTest(scraper=module):
                with self.assertRaisesRegex(boards.ScraperError, company):
                    self.scrape(module)

    def test_bad_payloads_are_not_reported_as_empty_results(self):
        for module in ("reddit", "zapier", "spotify", "github", "oracle", "tiktok", "redfin"):
            with self.subTest(scraper=module):
                self.session.get.return_value = response({"error": "board changed"})
                self.session.post.return_value = response({"error": "board changed"})
                with self.assertRaises(boards.ScraperError):
                    self.scrape(module)

    def test_missing_new_job_description_is_an_error(self):
        job = greenhouse(1)
        job["content"] = ""
        self.session.get.return_value = response({"jobs": [job]})
        with self.assertRaisesRegex(boards.ScraperError, "Missing title or description"):
            self.scrape("reddit")

    def test_incomplete_oracle_detail_payload_is_an_explicit_error(self):
        self.session.get.side_effect = [
            oracle_page([oracle_listing("1")], 1), response({"items": []}),
        ]
        with self.assertRaisesRegex(boards.ScraperError, "Oracle"):
            self.scrape("oracle")

    def test_known_job_without_description_is_still_counted(self):
        job = greenhouse(1)
        job["content"] = ""
        self.session.get.return_value = response({"jobs": [job]})
        self.assertEqual(self.scrape("reddit", [1]), ([], 1))

    def test_tiktok_api_error_is_not_an_empty_success(self):
        self.session.post.return_value = response({"code": 500, "message": "Service unavailable"})
        with self.assertRaisesRegex(boards.ScraperError, "Service unavailable"):
            self.scrape("tiktok")

    def test_jibe_repeated_page_cannot_loop_forever(self):
        self.session.get.return_value = response({"jobs": [jibe("1")], "totalCount": 2})
        with self.assertRaisesRegex(boards.ScraperError, "Pagination stopped"):
            self.scrape("github")
        self.assertEqual(self.session.get.call_count, 2)

    def test_empty_paginated_feeds_are_valid(self):
        cases = {
            "github": response({"jobs": [], "totalCount": 0}),
            "oracle": oracle_page([], 0),
            "spotify": response([]),
            "tiktok": tiktok_page([], 0),
            "hulu": response(html='<ul id="search-results-jobs" data-results-count="0"></ul>'),
        }
        for module, result in cases.items():
            with self.subTest(scraper=module):
                self.session.get.return_value = result
                self.session.post.return_value = result
                self.assertEqual(self.scrape(module), ([], 0))

    def test_missing_workday_employer_is_explicit(self):
        self.session.post.return_value = response({"facets": [{
            "facetParameter": "hiringCompany",
            "values": [{"descriptor": "Rocket Mortgage", "id": "other"}],
        }]})
        with self.assertRaisesRegex(boards.ScraperError, "Redfin Corporation"):
            self.scrape("redfin")

    def test_linkedin_login_and_missing_description_are_explicit(self):
        self.session.get.return_value = response(html="<title>Sign In</title><form></form>")
        with self.assertRaisesRegex(boards.ScraperError, "login or challenge"):
            self.scrape("linkedin")
        self.session.get.side_effect = [
            response(html=linkedin_card(1)), response(html="<h1>Sign In</h1>"),
        ]
        with self.assertRaisesRegex(boards.ScraperError, "description missing"):
            self.scrape("linkedin")

    def test_websites_distinguish_no_openings_from_broken_markup(self):
        self.session.get.return_value = response(html="<h1>No open positions</h1>")
        self.assertEqual(self.scrape("serpapi"), ([], 0))
        self.session.get.return_value = response(html="<h1>Access denied</h1>")
        with self.assertRaisesRegex(boards.ScraperError, "No job links"):
            self.scrape("serpapi")

    def test_hulu_missing_results_are_explicit(self):
        self.session.get.return_value = response(html="<h1>Access denied</h1>")
        with self.assertRaisesRegex(boards.ScraperError, "results missing"):
            self.scrape("hulu")


if __name__ == "__main__":
    unittest.main()
