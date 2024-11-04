from playwright.sync_api import sync_playwright, Page, Locator
from .utils import log, queries
import time
from datetime import datetime
import re

def getJobDetails(job_id: str, link: Locator, page: Page):
    """Get job details from a given URL"""
    details = {
        'company': 'Salesforce',
        'job_id': job_id,
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
        'location': 'Seattle, WA',
        'link': link,
    }

    try:

        page.goto(link)
        time.sleep(1)  # Wait for the page to load
        # Get the job title
        details['title'] = page.locator('h1.hero-heading').text_content()
        posted = page.locator('time')
        details['date_posted'] = posted.get_attribute('datetime')
        description = page.locator('article.cms-content').text_content()
        job_meta = page.locator('ul.job-meta li').all()
        pay = []

        for meta in job_meta:
            if re.search('\\$', meta.text_content()):
                pay.append(meta.text_content())
        pay = '. '.join(pay)
        details['description'] = description + pay
        return details
    
    except Exception as e:
        log("Error getting job details: {e}".format(e=e), "error")

def getJobs(query: str, job_ids: list[int]) -> list[dict]:
    query_url = f"https://careers.salesforce.com/en/jobs/?search={query}&country=United+States+of+America&region=Washington&type=Full+time&jobtype=Regular&pagesize=50#results"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(1) # Wait for the page to load

            result_list = page.locator("div.card-job h3 a").all()
            if len(result_list) == 0:
                log("Unable to connect to Salesforce.", "error")

            else:
                jobs_found = len(result_list)
                result_list = [f"https://careers.salesforce.com{link.get_attribute('href')}" for link in result_list]

                for link in result_list:
                    job_id = re.search(r'jobs\/([^\/]*)', link)
                    if job_id is not None and job_id.group(1) is not None:
                        job_id = job_id.group(1)
                        if job_id not in job_ids:
                            jobDetails = getJobDetails(job_id, link, page)
                            if 'job_id' in jobDetails and jobDetails['job_id'] not in job_ids:
                                jobs.append(jobDetails)

        except Exception as e:
            log(f"Error fetching jobs from Salesforce: {e}")

        finally:
            browser.close()

    return jobs, jobs_found

def getSalesforceJobs(job_ids: list[int]):
    log("Fetching jobs for Salesforce...")
    jobs = []
    total_jobs = 0

    for query in queries:
        job_results, jobs_found = getJobs(query, job_ids)
        total_jobs += jobs_found
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

    log("Total number of new positions found for Salesforce: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
