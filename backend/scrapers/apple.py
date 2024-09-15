from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page
import time
import re

def getJobDetails(job_id: str, browser):
    url = "https://jobs.apple.com/en-us/details/{job_id}"
    page = browser.new_page()
    page.goto(url.format(job_id=job_id))

    min_qualifications = ""
    preferred_qualifications = ""

    title = page.locator("h1").text_content().strip()
    location = page.locator("div#job-location-name").text_content().strip()
    team = page.locator("div#job-team-name").text_content().strip()
    date_posted = page.locator("time#jobPostDate").text_content().strip()
    summary = page.locator("div#jd-job-summary").text_content().strip()
    job_description = page.locator("div#jd-description").text_content().strip()
    if page.query_selector("div#jd-minimum-qualifications"):
        min_qualifications = page.locator("div#jd-minimum-qualifications").text_content().strip
    elif page.query_selector("div#jd-key-qualifications"):
        min_qualifications = page.locator("div#jd-key-qualifications").text_content().strip()

    if page.query_selector("div#jd-preferred-qualifications"):
        preferred_qualifications = page.locator("div#jd-preferred-qualifications").text_content().strip
    description = "{summary} {job_description} {min_qualifications} {preferred_qualifications}".format(summary=summary, job_description=job_description, min_qualifications=min_qualifications, preferred_qualifications=preferred_qualifications)

    details = {
        'job_id': job_id,
        'title': title,
        'location': location,
        'date_posted': date_posted,
        'summary': summary,
        'min_qualifications': min_qualifications,
        'preferred_qualifications': preferred_qualifications,
        'job_description': job_description,
        'description': description,
        'team': team,
        'link': "https://jobs.apple.com/en-us/details/{id}".format(id=job_id),
    }


    return details


def getJobs(query):
    query_url = "https://jobs.apple.com/en-us/search?search={query}&sort=newest&location=seattle-SEA"
    url = query_url.format(query=query)
    jobs = []
    job_cells = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        results_table = page.locator('div.results__table')
        job_cells = results_table.locator('tbody').all()

        for cell in job_cells:
            cell_id = cell.get_attribute('id')
            job_id = re.split(r'[\-_]', cell_id)
            if (job_id and len(job_id) > 2):
                job_details = getJobDetails(job_id[2], browser)
                jobs.append(job_details)

        browser.close()

    return jobs


def getAppleJobs():
    print("Fetching jobs for Apple...")
    base_url = "https://jobs.apple.com/en-us/search?location=united-states-USA"
    queries = ["web", "engineering", "frontend"]
    jobs = []

    for query in queries:
        job_results = getJobs(query)
        print("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if (len(jobs) == 0):
            jobs = job_results
        else:
            for job in job_results:
                found = False
                for existing_job in jobs:
                    if (existing_job['job_id'] == job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

        time.sleep(5)

    print("Total number of positions found: {count}".format(count=len(jobs)))
    return job_results