from playwright.sync_api import sync_playwright, Page, Locator
from .utils import Extractor, log, queries
import time
from datetime import datetime
import re

def getJobDetails(url: str, page: Page):
    # Get job id from URL
    jobId = re.search('jobs/results/(\d+)', url).group(1)
    url = "https://www.google.com/about/careers/applications/" + url
    details = {
        'job_id': jobId,
        'link': url,
        'company': 'Google',
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
        'date_posted': datetime.now().strftime("%Y-%m-%d")
    }

    try:
        page.goto(url)
        main = page.locator("main")
        title = main.locator("h2").all()
        if title and len(title) > 0:
            title = title[0].text_content().strip()
            details['title'] = title

        meta = main.locator("i ~ span").all()
        locations = ""
        for item in meta:
            text = item.text_content().strip()
            if text != "Google" and text != "Mid" and " more" not in text and text != "Advanced":
                locations += text

        details['location'] = locations

        # Get description
        description_blocks = main.locator('div[data-id="{jobId}"] > div'.format(jobId=jobId)).all()
        description = ""

        for block in description_blocks:
            header = block.locator("h3")

            if header.count() > 0:
                headStart = False
                elements = block.locator(">*").all()

                for element in elements:
                    tag_name = element.evaluate("el => el.tagName").lower()
                    if tag_name == 'h3':
                        headStart = True
                    if headStart:        
                        description += element.text_content().strip() + "\n"

        details['description'] = description

    except Exception as e:
        log("Error getting job details for: \"" + url + "\" " + str(e), "error")

    return details


def getJobs(query: str, job_ids: list[int]):
    query_url = "https://www.google.com/about/careers/applications/jobs/results?location=Washington%2C%20USA&q={query}&sort_by=date"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2)

            main = page.locator("main")

            job_cards = main.locator("li.lLd3Je").all()
            job_links = [card.locator("a").get_attribute("href") for card in job_cards]

            for link in job_links:
                jobDetails = getJobDetails(link, page)
                jobs.append(jobDetails)

        except Exception as e:
            log("Error fetching Google jobs: " + str(e), "error")

        finally:
            browser.close()

    return jobs


def getGoogleJobs(job_ids: list[str]):
    log("Fetching jobs for Google...")
    jobs = []

    for query in queries:
        job_results = getJobs(query, job_ids)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if len(job_results) == 0:
            jobs = job_results
        else:
            for job in job_results:
                found = False
                for existing_job in jobs:
                    if job['job_id'] == existing_job['job_id']:
                        found = True
                        break
                if not found:
                    jobs.append(job)

    log("Total number of positions foundfor Google: {count}".format(count=len(jobs)))

    return jobs
