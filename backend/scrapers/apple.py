from playwright.sync_api import sync_playwright, Page
from .scraper_utils import Extractor, log, get_queries
import time
import re

def getJobDetails(job_id: str, page):
    details = {}
    try:
        url = f"https://jobs.apple.com/en-us/details/{job_id}"
        page.goto(url)
        time.sleep(3)
        extract = Extractor(page, "Apple", job_id)

        title = extract.getText("h1")
        location = extract.getText("label#jobdetails-joblocation", True)
        team = extract.getText("label#jobdetails-teamname", True)
        date_posted = extract.getText("time#jobdetails-jobpostdate", True)
        summary = extract.getText("div#jobdetails-jobdetails-jobsummary-content-row", True)
        job_description = extract.getText("div#jobdetails-jobdetails-jobdescription-content-row", True)
        min_qualifications = extract.getText("div#jobdetails-jobdetails-minimumqualifications-content-row")
        preferred_qualifications = extract.getText("div#jobdetails-jobdetails-preferredqualifications-content-row")

        description = "{summary} {job_description} {min_qualifications} {preferred_qualifications}".format(summary=summary, job_description=job_description, min_qualifications=min_qualifications, preferred_qualifications=preferred_qualifications)

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
    new_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(3)

            result_set = page.locator('section#search-result-set')
            if result_set:
                job_listings = result_set.locator('li.rc-accordion-item').all()

                if job_listings:
                    jobs_found = len(job_listings)
                    for listing in job_listings:
                        anchor = listing.locator('h3 a').all()
                        link = anchor[0].get_attribute('href')
                        job_id = re.search(r'/details/(\d+)/', link).group(1)
                        if job_id:
                            if job_id not in job_ids:
                                new_jobs.append(job_id)

        except Exception as e:
            log(f"Problems parsing jobs for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")

        
        for job in new_jobs:
            job_details = getJobDetails(job, page)
            jobs.append(job_details)

        browser.close()

    return jobs, jobs_found


def getAppleJobs(job_ids):
    log("Fetching jobs for Apple...")
    jobs = []
    total_found = 0
    queries = get_queries()

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
                    if 'job_id' in job and 'job_id' in existing_job and existing_job['job_id'] == job['job_id']:
                        found = True
                        break
                if found == False:
                    jobs.append(job)

    log("Total number of new positions found for Apple: {count}/{total_found}".format(count=len(jobs), total_found=total_found))
    return jobs

if __name__ == "__main__": 
    getAppleJobs([])