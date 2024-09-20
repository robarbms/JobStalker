from playwright.sync_api import sync_playwright, Page
from .utils import Extractor, log, queries
import time
import re

def getJobDetails(job_id: str, browser):
    details = {}
    try:
        url = "https://jobs.apple.com/en-us/details/{job_id}"
        page = browser.new_page()
        page.goto(url.format(job_id=job_id))
        extract = Extractor(page, "Apple", job_id)

        title = extract.getText("h1")
        location = extract.getText("div#job-location-name", True)
        team = extract.getText("div#job-team-name", True)
        date_posted = extract.getText("time#jobPostDate", True)
        summary = extract.getText("div#jd-job-summary", True)
        job_description = extract.getText("div#jd-description", True)
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
    except:
        log("Failed to parse job details for {id}".format(id=job_id), "error")


    return details


def getJobs(query, job_ids):
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
                    if job_id and len(job_id) > 2:
                        if str(job_id[2]) in job_ids:
                            print('Found job:', str(job_id[2]))
                        else:
                            job_details = getJobDetails(job_id[2], browser)
                            jobs.append(job_details)

        browser.close()

    return jobs


def getAppleJobs(job_ids):
    log("Fetching jobs for Apple...")
    base_url = "https://jobs.apple.com/en-us/search?location=united-states-USA"
    jobs = []

    for query in queries:
        job_results = getJobs(query, job_ids)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if (len(jobs) == 0):
            jobs = job_results
        else:
            for job in job_results:
                found = False
                for existing_job in jobs:
                    if (job and 'job_id' in job and existing_job and 'job_id' in existing_job and existing_job['job_id'] == job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

        time.sleep(1)

    log("Total number of positions found: {count}".format(count=len(jobs)))
    return job_results