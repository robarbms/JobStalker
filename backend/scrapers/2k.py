from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
import datetime


def getJobs(page: Page):
    url = "https://2k.com/careers/"
    jobs = []

    try:
        page.goto(url)
        time.sleep(3)

        listings = page.locator('data.bc-career-card').all()
        for listing in listings:
            pass

    except Exception as e:
        log("Could not fetch results from 2k", "error")
        log(str(e), "error")

    finally:
        return jobs

"""
    Gets jobs based on a list of queries
    Args:
    - job_ids: List of job IDs already in the database
"""
def get2kJobs(job_ids: list[str]):
    log("Fetching jobs for 2k...", "info", no_end=True)
    jobs = []
    total_jobs = 0

    # 2k doesn't support queries so I will manually search through results
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_default_timeout(6000)
        jobs_found = 0

        job_postings = getJobs(page)

    # for query in queries:
    #     job_results, jobs_found = getJobs(query, job_ids)
    #     total_jobs += jobs_found

    #     job_ids += [job['job_id'] for job in job_results]
    #     jobs += job_results

    #     time.sleep(3)

    return jobs
