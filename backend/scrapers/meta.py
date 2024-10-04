from playwright.sync_api import sync_playwright, Page, Locator
from .utils import Extractor, log, queries
import time
import datetime
import re
from bs4 import BeautifulSoup

def getJobDetails(link: Locator, page: Page):
    """Get job details from a given URL"""
    details = {
        'company': 'Meta',
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
    }

    try:

        with page.expect_popup() as popup_info:
            link.click()

        new_page = popup_info.value
        time.sleep(3)  # Wait for the new page to load

        title = new_page.locator("div._9ata._8ww0")

        if title.is_visible():
            details['title'] = title.text_content()

        url = new_page.url
        details['link'] = url
        job_id = re.search(r'jobs/(\d+)/', url).group(1)
        details['job_id'] = job_id

        print(details)
        return details
    
    except Exception as e:
        log("Error getting job details: {e}".format(e=e), "error")

    

def getJobs(query: str, job_ids: list[int]) -> list[dict]:
    """Get jobs from a given query"""
    query_url = "https://www.metacareers.com/jobs?q={query}&offices[0]=Seattle%2C%20WA"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(5) # Wait for the page to load

            print(page.inner_html('body'))

            result_list = page.locator("div[role=link]").all()
            if len(result_list) == 0:
                log("Unable to connect to Meta.", "error")
                return []

            print(url, len(result_list))

            for link in result_list:
                jobDetails = getJobDetails(link, page)
                break

        except Exception as e:
            log(f"Error fetching jobs from Meta: {e}")

        finally:
            browser.close()

    return jobs

def getMetaJobs(job_ids: list[int]):
    log("Fetching jobs for Meta...")
    jobs = []

    for query in queries:
        job_results = getJobs(query, job_ids)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))
        return jobs
