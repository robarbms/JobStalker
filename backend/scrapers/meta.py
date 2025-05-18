from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
from datetime import datetime
import re

def getJobDetails(link: Locator, page: Page):
    """Get job details from a given URL"""
    details = {
        'company': 'Meta',
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
        'location': 'Seattle, WA',
        'date_posted': datetime.now().strftime("%Y-%m-%d")
    }

    try:

        with page.expect_popup() as popup_info:
            link.click()

        new_page = popup_info.value
        time.sleep(5)  # Wait for the new page to load

        title = new_page.locator("div._9ata._8ww0")

        if title.is_visible():
            details['title'] = title.text_content()

        url = new_page.url
        details['link'] = url
        job_id = re.search(r'jobs/(\d+)/', url).group(1)
        details['job_id'] = job_id
        description = ""
        description_conts = new_page.locator("div._8lfv div._8muv > div > div").all()
        for cont in description_conts:
            description += cont.text_content() + "\n\n"

        details['description'] = description

        return details
    
    except Exception as e:
        log("Error getting job details: {e}".format(e=e), "error")

    

def getJobs(query: str, job_ids: list[int]) -> list[dict]:
    """Get jobs from a given query"""
    query_url = "https://www.metacareers.com/jobs?offices[0]=Bellevue%2C%20WA&offices[1]=Seattle%2C%20WA&offices[2]=Redmond%2C%20WA&q={query}&sort_by_new=true"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(5) # Wait for the page to load

            result_list = page.locator("div[role=link]").all()
            if len(result_list) == 0:
                log("Unable to connect to Meta.", "error")

            else:
                jobs_found = len(result_list)

                for link in result_list:
                    jobDetails = getJobDetails(link, page)
                    if 'job_id' in jobDetails and jobDetails['job_id'] not in job_ids:
                        jobs.append(jobDetails)

        except Exception as e:
            log(f"Error fetching jobs from Meta: {e}")

        finally:
            browser.close()

    return jobs, jobs_found

def getMetaJobs(job_ids: list[int]):
    log("Fetching jobs for Meta...")
    jobs = []
    total_jobs = 0
    queries = get_queries()

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

    log("Total number of new positions found for Meta: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
