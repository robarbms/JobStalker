"""Offline DOM fixtures exercise the legacy Playwright scrapers without a browser."""

from contextlib import ExitStack
import importlib
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from bs4 import BeautifulSoup


LEGACY_SCRAPERS = {
    "adobe": "getAdobeJobs",
    "airbnb": "getAirbnbJobs",
    "amazon": "getAmazonJobs",
    "apple": "getAppleJobs",
    "atlassian": "getAtlassianJobs",
    "blizzard": "getBlizzardJobs",
    "expedia": "getExpediaJobs",
    "google": "getGoogleJobs",
    "meta": "getMetaJobs",
    "microsoft": "getMicrosoftJobs",
    "netflix": "getNetflixJobs",
    "nvidia": "getNvidiaJobs",
    "salesforce": "getSalesforceJobs",
}


class FixtureLocator:
    def __init__(self, nodes):
        self.nodes = nodes

    def __getitem__(self, index):
        return FixtureLocator([self.nodes[index]])

    def locator(self, selector):
        if selector.startswith(">"):
            selector = ":scope " + selector
        return FixtureLocator([child for node in self.nodes for child in node.select(selector)])

    def all(self):
        return [FixtureLocator([node]) for node in self.nodes]

    def count(self):
        return len(self.nodes)

    def text_content(self):
        return self.nodes[0].get_text()

    def inner_text(self):
        return self.nodes[0].get_text(" ", strip=True)

    def inner_html(self):
        return self.nodes[0].decode_contents()

    def get_attribute(self, name):
        return self.nodes[0].get(name)

    def is_visible(self):
        return bool(self.nodes)

    def evaluate(self, expression):
        return self.nodes[0].name.upper()

    def click(self):
        pass

    def fill(self, value):
        pass

    def select_option(self, value):
        pass

    def dispatch_event(self, event):
        pass


class FixturePage:
    def __init__(self, html, details=None):
        self.html = html
        self.details = details or {}
        self.soup = BeautifulSoup(html, "html.parser")
        self.url = "https://example.com"
        self.popup = None

    def goto(self, url):
        self.url = url
        self.soup = BeautifulSoup(self.details.get(url, self.html), "html.parser")

    def locator(self, selector):
        return FixtureLocator(self.soup.select(selector))

    def query_selector(self, selector):
        return self.soup.select_one(selector)

    def content(self):
        return str(self.soup)

    def set_default_timeout(self, timeout):
        pass

    def close(self):
        pass

    def expect_popup(self):
        context = MagicMock()
        context.__enter__.return_value = context
        context.value = self.popup
        return context


class ExistingScraperTests(unittest.TestCase):
    def run_scraper(self, module_name, html, details=None, ids=None, function="getJobs", popup=None):
        module = importlib.import_module(f"backend.scrapers.{module_name}")
        page = FixturePage(html, details)
        page.popup = popup
        browser = Mock()
        browser.new_page.return_value = page
        playwright = MagicMock()
        playwright.__enter__.return_value.chromium.launch.return_value = browser
        with ExitStack() as stack:
            stack.enter_context(patch.object(module, "sync_playwright", return_value=playwright))
            stack.enter_context(patch.object(module.time, "sleep"))
            logger = stack.enter_context(patch.object(module, "log"))
            if hasattr(module, "Locator"):
                stack.enter_context(patch.object(module, "Locator", FixtureLocator))
            if module_name in ("airbnb", "atlassian", "expedia"):
                result = getattr(module, LEGACY_SCRAPERS[module_name])(
                    [] if ids is None else ids, ["engineer"],
                )
            elif module_name in ("zillow", "2k"):
                result = getattr(module, function)([] if ids is None else ids)
            else:
                result = getattr(module, function)("engineer", [] if ids is None else ids)
            errors = [
                call for call in logger.call_args_list
                if "error" in call.args[1:] or call.kwargs.get("level") == "error"
            ]
            self.assertEqual(errors, [], f"{module_name} swallowed a fixture parsing error")
        return result, browser

    def assert_job(self, result, company, job_id="2", count=2):
        jobs, found = result
        self.assertEqual(found, count)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], company)
        self.assertEqual(jobs[0]["job_id"], job_id)
        self.assertEqual(jobs[0]["title"], "Software Engineer")
        self.assertIn("Build services", jobs[0]["description"])
        self.assertTrue(jobs[0]["link"].startswith("https://"))
        return jobs[0]

    def test_amazon_listings_and_details(self):
        html = "".join(
            f'<div class="job"><h3><a href="/en/jobs/{job_id}/engineer">Software Engineer</a></h3>'
            '<span class="posting-date">Posted October 25, 2026</span></div>'
            for job_id in ("1", "2")
        )
        details = {
            "https://www.amazon.jobs/en/jobs/2/engineer":
                '<div id="job-detail-body"><div>Build services</div></div>'
                '<div class="sidebar"><div class="row"><ul><li>Seattle, WA</li><li>AWS</li>'
                '</ul></div></div>',
        }
        result, browser = self.run_scraper("amazon", html, details, ["1"])
        job = self.assert_job(result, "Amazon")
        self.assertEqual(job["location"], "Seattle, WA")
        self.assertEqual(job["team"], "AWS")
        browser.close.assert_called_once()

    def test_apple_listings_and_details(self):
        html = '<section id="search-result-set">' + "".join(
            f'<li class="rc-accordion-item"><h3><a href="/en-us/details/{job_id}/engineer">'
            'Software Engineer</a></h3></li>' for job_id in ("1", "2")
        ) + '</section>'
        details = {"https://jobs.apple.com/en-us/details/2": """
            <h1>Software Engineer</h1><label id="jobdetails-joblocation">Seattle, WA</label>
            <label id="jobdetails-teamname">Engineering</label>
            <time id="jobdetails-jobpostdate">Oct 25, 2026</time>
            <div id="jobdetails-jobdetails-jobsummary-content-row">Build services</div>
            <div id="jobdetails-jobdetails-jobdescription-content-row">Operate services</div>
        """}
        result, browser = self.run_scraper("apple", html, details, ["1"])
        job = self.assert_job(result, "Apple")
        self.assertEqual(job["location"], "Seattle, WA")
        self.assertIn("Operate services", job["description"])
        browser.close.assert_called_once()

    def test_google_listings_and_details(self):
        html = '<main>' + "".join(
            f'<li class="lLd3Je"><a href="jobs/results/{job_id}-engineer">Software Engineer</a></li>'
            for job_id in ("1", "2")
        ) + '</main>'
        details = {
            "https://www.google.com/about/careers/applications/jobs/results/2-engineer": """
            <main><h2>Software Engineer</h2><i></i><span>Seattle, WA</span>
            <div data-id="2"><div><h3>Responsibilities</h3><p>Build services</p></div></div></main>
            """,
        }
        result, browser = self.run_scraper("google", html, details, ["1"])
        job = self.assert_job(result, "Google")
        self.assertIn("Seattle", job["location"])
        browser.close.assert_called_once()

    def test_microsoft_listings_and_details(self):
        html = '<main>' + "".join(
            f'<div data-test-id="job-listing"><a href="/careers/job/{job_id}">Software Engineer</a></div>'
            for job_id in ("1", "2")
        ) + '</main>'
        details = {"https://apply.careers.microsoft.com/careers/job/2": """
            <h2 class="position-title-example">Software Engineer</h2>
            <div class="detailContainer-example">
            <div class="detailLabel-example">Date posted</div>
            <div class="detailValue-example">2026-10-25</div></div>
            <div class="detailContainer-example">
            <div class="detailLabel-example">Work site</div>
            <div class="detailValue-example">Remote</div></div>
            <div id="job-description-container"><p>Build services</p></div>
        """}
        result, browser = self.run_scraper("microsoft", html, details, ["1"])
        job = self.assert_job(result, "Microsoft")
        self.assertEqual(job["date_posted"], "2026-10-25")
        self.assertEqual(job["location"], "Remote")
        browser.close.assert_called_once()

    def test_adobe_listings_and_description(self):
        html = """
            <select></select><button aria-controls="CityBody"></button>
            <input id="facetInput_3"><input aria-label="Seattle">
        """ + "".join(
            f'<li class="jobs-list-item"><span class="jobId"><span>ID</span><i></i>'
            f'<span>{job_id}</span></span><span role="heading">'
            f'<a href="https://careers.adobe.com/us/en/job/{job_id}">Software Engineer</a></span>'
            '<span class="job-postdate">Posted Date 10/25/2026</span></li>'
            for job_id in ("1", "2")
        )
        details = {"https://careers.adobe.com/us/en/job/2":
                   '<div class="jd-info"><p>Header</p><p>Company</p><p>Build services</p></div>'}
        result, browser = self.run_scraper("adobe", html, details, ["1"])
        self.assert_job(result, "Adobe")
        self.assertEqual(browser.close.call_count, 2)

    def test_airbnb_listings_and_details(self):
        html = "".join(
            f'<a href="https://careers.airbnb.com/positions/{job_id}/">Software Engineer</a>'
            for job_id in ("1", "2")
        )
        details = {"https://careers.airbnb.com/positions/2/": """
            <h1>Software Engineer</h1><script>{"datePublished":"2026-10-25"}</script>
            <div class="job-detail"><p>Build services</p><p>Your Location:</p><p>Not description</p></div>
        """}
        result, _ = self.run_scraper("airbnb", html, details, ["1"])
        job = self.assert_job(result, "Airbnb")
        self.assertEqual(job["date_posted"], "2026-10-25")
        self.assertNotIn("Not description", job["description"])

    def test_atlassian_listings_salary_and_details(self):
        html = '<div class="careers"><table><tr><th>Title</th></tr>' + "".join(
            f'<tr><td><a href="/company/careers/details/{job_id}">Software Engineer</a></td></tr>'
            for job_id in ("1", "2")
        ) + '</table></div>'
        details = {"https://www.atlassian.com/company/careers/details/2": """
            <h1 class="default heading">Software Engineer</h1><div class="column"></div>
            <div class="column"><p>Build services</p><p>Compensation</p>
            <p>$120,000 - $180,000</p></div>
        """}
        result, _ = self.run_scraper("atlassian", html, details, ["1"])
        job = self.assert_job(result, "Atlassian")
        self.assertEqual((job["salary_min"], job["salary_max"]), ("120000", "180000"))
        self.assertEqual(job["location"], "")

    def test_expedia_listings_and_metadata(self):
        html = '<div class="Results__list__content">' + "".join(
            f'<a href="/job/{job_id}/">Software Engineer</a>' for job_id in ("1", "2")
        ) + '</div>'
        details = {"https://careers.expediagroup.com/job/2/": """
            <h1 class="Desc__title">Software Engineer</h1>
            <ul class="Info__list"><p>Seattle, WA</p><p>Engineering</p><p>Full time</p>
            <p>10/25/2026</p><p>ID # 2</p></ul><div class="Desc__copy">Build services</div>
        """}
        result, _ = self.run_scraper("expedia", html, details, ["1"])
        job = self.assert_job(result, "Expedia")
        self.assertEqual(job["date_posted"], "2026-10-25")

    def test_nvidia_listings_and_workday_details(self):
        html = '<section><ul>' + "".join(
            f'<li><a href="/en-US/job/engineer/{job_id}">Software Engineer</a>'
            f'<ul>{job_id}</ul></li>' for job_id in ("1", "2")
        ) + '</ul></section>'
        details = {"https://nvidia.wd5.myworkdayjobs.com/en-US/job/engineer/2": """
            <h2 data-automation-id="jobPostingHeader">Software Engineer</h2>
            <dl><dt>locations</dt><dd>Seattle, WA</dd><dd>Remote</dd></dl>
            <dl><dt>posted on</dt><dd>Posted Today</dd></dl>
            <dl><dt>job requisition id</dt><dd>2</dd></dl>
            <div data-automation-id="jobPostingDescription">Build services</div>
        """}
        result, browser = self.run_scraper("nvidia", html, details, ["1"])
        job = self.assert_job(result, "Nvidia")
        self.assertEqual(job["location"], "Seattle, WA - Remote")
        browser.close.assert_called_once()

    def test_netflix_listing_metadata_and_position_html(self):
        positions = {"positions": [{
            "display_job_id": "2", "locations": [],
            "canonicalPositionUrl": "https://jobs.netflix.com/jobs/2",
        }]}
        html = """
            <div class="card">Software Engineer</div>
            <div class="position-container"><h1 class="position-title">Software Engineer</h1>
            <p class="position-location"><span>Remote</span></p>
            <div class="custom-jd-container">
            <div class="custom-jd-field"><h4>Job ID</h4><div>2</div></div>
            <div class="custom-jd-field"><h4>Date Posted</h4><div>2026-10-25</div></div>
            <div class="custom-jd-field"><h4>Teams</h4><div>Engineering</div></div></div>
            <div class="position-job-description"><ul><li>Build services</li></ul></div></div>
        """ + '<script>' + json.dumps(positions) + '</script>'
        result, browser = self.run_scraper("netflix", html)
        job = self.assert_job(result, "Netflix", count=1)
        self.assertEqual(job["team"], "Engineering")
        browser.close.assert_called_once()
        result, _ = self.run_scraper("netflix", html, ids=["2"])
        self.assertEqual(result, ([], 1))

    def test_meta_popup_details_and_known_ids(self):
        html = '<a role="link">Software Engineer</a>'
        popup = FixturePage("""
            <div class="_9ata _8ww0">Software Engineer</div>
            <div class="_8lfv"><div class="_8muv"><div><div>Build services</div></div></div></div>
        """)
        popup.url = "https://www.metacareers.com/jobs/2/"
        result, browser = self.run_scraper("meta", html, popup=popup)
        self.assert_job(result, "Meta", count=1)
        browser.close.assert_called_once()
        result, _ = self.run_scraper("meta", html, ids=["2"], popup=popup)
        self.assertEqual(result, ([], 1))

    def test_salesforce_listings_and_pay_description(self):
        html = "".join(
            f'<div class="card-job" href="/jobs/{job_id}">Software Engineer</div>'
            for job_id in ("1", "2")
        )
        details = {"https://careers.salesforce.com/jobs/2": """
            <h1 class="hero-heading">Software Engineer</h1><time datetime="2026-10-25"></time>
            <article class="cms-content">Build services</article>
            <ul class="job-meta"><li>$120,000 - $180,000</li></ul>
        """}
        result, browser = self.run_scraper("salesforce", html, details, ["1"])
        job = self.assert_job(result, "Salesforce")
        self.assertIn("$120,000", job["description"])
        browser.close.assert_called_once()

    def test_blizzard_filters_locations_and_known_jobs(self):
        html = "".join(
            '<li class="jobs-list-item"><span class="job-location"><span>Location</span>'
            f'<span>{location}</span></span><span class="jobId"><span>ID</span>'
            f'<span>{job_id}</span></span><div class="job-title"><span>Software Engineer</span></div>'
            '<span class="job-postdate">Posted Date 10/25/2026</span>'
            f'<a href="https://careers.blizzard.com/job/{job_id}">Details</a></li>'
            for job_id, location in (("1", "United States"), ("2", "United States"), ("3", "France"))
        )
        details = {"https://careers.blizzard.com/job/2":
                   '<div class="jd-info"><div>Build services</div></div>'}
        result, browser = self.run_scraper("blizzard", html, details, ["1"])
        self.assert_job(result, "Blizzard", count=3)
        browser.close.assert_called_once()

    def test_zillow_listings_details_and_known_ids(self):
        html = '<ul role="list" aria-label="Page 1 of 1">' + "".join(
            f'<li><div><h3><a href="job/engineer/{job_id}">Software Engineer</a></h3></div>'
            '<div><dd>Posted Today</dd></div><div><dd>Seattle, WA</dd></div>'
            f'<ul><li>{job_id}</li></ul></li>' for job_id in ("1", "2")
        ) + '</ul><div data-automation-id="jobPostingDescription">Build services</div>'
        result, browser = self.run_scraper("zillow", html, ids=["1"], function="getZillowJobs")
        job = self.assert_job(result, "Zillow")
        self.assertEqual(job["location"], "Seattle, WA")
        browser.close.assert_called_once()

    def test_zillow_uses_detail_locations_for_multi_location_listings(self):
        html = """
            <ul role="list" aria-label="Page 1 of 1"><li>
            <div><h3><a href="job/engineer/2">Software Engineer</a></h3></div>
            <div><dd>Posted Today</dd></div><div><dd>2 Locations</dd></div>
            <ul><li>2</li></ul></li></ul>
            <dl><dt>locations</dt><dd>Austin, TX</dd><dd>Seattle, WA</dd></dl>
            <div data-automation-id="jobPostingDescription">Build services</div>
        """
        result, _ = self.run_scraper("zillow", html, function="getZillowJobs")
        job = self.assert_job(result, "Zillow", count=1)
        self.assertEqual(job["location"], "Austin, TX; Seattle, WA")

    def test_existing_entry_points_load_configured_queries(self):
        for module_name, function in LEGACY_SCRAPERS.items():
            with self.subTest(scraper=module_name):
                module = importlib.import_module(f"backend.scrapers.{module_name}")
                with ExitStack() as stack:
                    config = stack.enter_context(patch.object(module, "get_queries", return_value=["engineer"]))
                    stack.enter_context(patch.object(module, "log"))
                    stack.enter_context(patch.object(module.time, "sleep"))
                    if module_name in ("airbnb", "atlassian", "expedia"):
                        source = "getJobIds" if module_name == "atlassian" else "getJobs"
                        value = (["2"], 3, {}) if module_name == "airbnb" else (["2"], 3)
                        stack.enter_context(patch.object(module, source, return_value=value))
                        stack.enter_context(patch.object(module, "getJobDetails", return_value={"job_id": "2"}))
                    else:
                        stack.enter_context(patch.object(module, "getJobs", return_value=([{"job_id": "2"}], 3)))
                    result = getattr(module, function)([], None)
                config.assert_called_once_with()
                self.assertEqual(result, ([{"job_id": "2"}], 3))

    def test_existing_scrapers_release_browser_on_navigation_failure(self):
        for module_name in (
            "adobe", "amazon", "apple", "blizzard", "google", "meta",
            "microsoft", "netflix", "nvidia", "salesforce",
        ):
            with self.subTest(scraper=module_name):
                module = importlib.import_module(f"backend.scrapers.{module_name}")
                playwright = MagicMock()
                browser = playwright.__enter__.return_value.chromium.launch.return_value
                browser.new_page.return_value.goto.side_effect = RuntimeError("Offline test")
                with patch.object(module, "sync_playwright", return_value=playwright), \
                     patch.object(module, "log") as logger, patch.object(module.time, "sleep"):
                    self.assertEqual(module.getJobs("engineer", []), ([], 0))
                browser.close.assert_called_once()
                logger.assert_called()

    def test_2k_unfinished_scraper_returns_no_jobs(self):
        result, _ = self.run_scraper(
            "2k", '<data class="bc-career-card">Software Engineer</data>', function="get2kJobs",
        )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
