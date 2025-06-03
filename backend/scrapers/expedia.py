from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
from datetime import datetime
import re

def getJobDetails(url: str):
    """Get job details from a given URL"""
    details = {
        'company': 'Expedia',
        'link': url,
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
        'location': 'Seattle, WA',
        'date_posted': datetime.now().strftime("%Y-%m-%d")
    }

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            title = page.locator('h4.Desc__title').text_content().strip()

            if title:
                details['title'] = title

            info = page.locator('ul.Info__list p').all()
            if info and len(info) >= 5:
                location = info[0].text_content().strip()
                details['location'] = location
                date_posted = info[3].text_content().strip()
                date_obj = datetime.strptime(date_posted, "%m/%d/%Y")
                details['date_posted'] = date_obj.strftime("%Y-%m-%d")
                id = info[4].text_content().strip()
                job_id = re.sub(r"ID *# *", "", id)
                details['job_id'] = job_id

            description = page.locator("div.Desc__copy").text_content().strip()
            details['description'] = description
    
        except Exception as e:
            log("Error getting job details: {e}".format(e=e), "error")

    return details

    

def getJobs(query: str, job_ids: list[int], job_links: list[str]) -> list[dict]:
    """Get jobs from a given query"""
    query_url = "https://careers.expediagroup.com/jobs/?keyword={query}&&filter[country]=United+States&filter[state]=Washington"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            result_list = page.locator(".Results__list__content a").all()
            jobs_found += len(result_list)
            for result_item in result_list:
                url = result_item.get_attribute('href')
                id_exists = False
                for id in job_ids:
                    if id in url:
                        id_exists = True
                        break
                if id_exists is False and url not in job_links:
                    jobs.append(url)

        except Exception as e:
            log(f"Error fetching jobs from Expedia: {e}")

        finally:
            browser.close()

    return jobs, jobs_found

def getExpediaJobs(job_ids: list[int]):
    log("Fetching jobs for Expedia...")
    jobs = []
    job_links = []
    total_jobs = 0
    queries = get_queries()

    for query in queries:
        new_jobs, jobs_found = getJobs(query, job_ids, job_links)
        total_jobs += jobs_found
        job_links += new_jobs

        log("Number of new positions found for \"{query}\": {count}/{jobs_found}".format(query=query, count=len(new_jobs), jobs_found=jobs_found))

    for link in job_links:
        jobDetails = getJobDetails(link)
        jobs.append(jobDetails)

    log("Total number of new positions found for Expedia: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
