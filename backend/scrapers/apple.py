from playwright.sync_api import sync_playwright, Page
from .utils import Extractor, log, queries
import time
import re

def getJobDetails(job_id: str, page):
    details = {}
    try:
        url = "https://jobs.apple.com/en-us/details/{job_id}"
        page.goto(url.format(job_id=job_id))
        time.sleep(3)
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
    except Exception as e:
        log("Failed to parse job details for {id}".format(id=job_id), "error")
        print(e)


    return details


def getJobs(query, job_ids):
    query_url = "https://jobs.apple.com/en-us/search?search={query}&sort=newest&location=seattle-SEA"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(3)

            results_table = page.locator('div.results__table')
            if results_table:
                job_cells = results_table.locator('tbody').all()

                if job_cells:
                    jobs_found = len(job_cells)
                    for cell in job_cells:
                        cell_id = cell.get_attribute('id')
                        job_id = re.split(r'[\-_]', cell_id)
                        if job_id and len(job_id) > 2:
                            if str(job_id[2]) not in job_ids:
                                job_details = getJobDetails(job_id[2], page)
                                jobs.append(job_details)

        except Exception as e:
            log(f"Problems parsing jobs for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")

        finally:
            browser.close()

    return jobs, jobs_found


def getAppleJobs(job_ids):
    log("Fetching jobs for Apple...")
    jobs = []
    total_found = 0

    for query in queries:
        job_results, jobs_found = getJobs(query, job_ids)
        total_found += jobs_found
        log("Number of new positions found for \"{query}\": {count}/{jobs_found}".format(query=query, count=len(job_results), jobs_found=jobs_found))

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

    log("Total number of new positions found for Apple: {count}/{total_found}".format(count=len(jobs), total_found=total_found))
    return job_results