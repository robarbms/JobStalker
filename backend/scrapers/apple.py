from playwright.sync_api import sync_playwright, Page
from .utils import Extractor, log
import time
import re

def getJobDetails(job_id: str, browser):
    url = "https://jobs.apple.com/en-us/details/{job_id}"
    page = browser.new_page()
    page.goto(url.format(job_id=job_id))
    extract = Extractor(page, "Apple", job_id)

    title = extract.getText("h1")
    location = extract.getText("div#job-location-name")
    team = extract.getText("div#job-team-name")
    date_posted = extract.getText("time#jobPostDate")
    summary = extract.getText("div#jd-job-summary")
    job_description = extract.getText("div#jd-description")
    min_qualifications = extract.getText("div#jd-minimum-qualifications")
    key_qualifications = extract.getText("div#jd-key-qualifications")
    preferred_qualifications = extract.getText("div#jd-preferred-qualifications")

    description = "{summary} {job_description} {min_qualifications} {preferred_qualifications} {key_qualifications}".format(summary=summary, job_description=job_description, min_qualifications=min_qualifications, preferred_qualifications=preferred_qualifications, key_qualifications=key_qualifications)

    details = {
        'job_id': job_id,
        'title': title,
        'location': location,
        'date_posted': date_posted,
        'min_qualifications': min_qualifications,
        'preferred_qualifications': preferred_qualifications,
        'job_description': job_description,
        'description': description,
        'team': team,
        'link': "https://jobs.apple.com/en-us/details/{id}".format(id=job_id),
        'salary_min': 0,
        'salary_max': 0,
        'notes': "",
        'summary': "",
        'company': 'Apple',
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
        if results_table:
            job_cells = results_table.locator('tbody').all()

            if job_cells:
                for cell in job_cells:
                    cell_id = cell.get_attribute('id')
                    job_id = re.split(r'[\-_]', cell_id)
                    if (job_id and len(job_id) > 2):
                        job_details = getJobDetails(job_id[2], browser)
                        jobs.append(job_details)

        browser.close()

    return jobs


def getAppleJobs():
    log("Fetching jobs for Apple...")
    base_url = "https://jobs.apple.com/en-us/search?location=united-states-USA"
    queries = ["web", "engineering", "prototype"]
    jobs = []

    for query in queries:
        job_results = getJobs(query)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

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

    log("Total number of positions found: {count}".format(count=len(jobs)))
    return job_results