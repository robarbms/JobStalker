from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
from datetime import datetime
import re

def getJobDetails(url: str, id: str):
    """Get job details from a given URL"""
    details = {
        'company': 'Atlassian',
        'job_id': id,
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

            title = page.locator('h1.default.heading').all()[0].text_content()
            if title:
                details['title'] = title
            text_block = page.locator('div.column').all()[1]
            
            paragraphs = text_block.locator('p').all()
            description = ""
            compensation_found = False
            for p in paragraphs:
                text = p.text_content()
                if (compensation_found == True):
                    salaries = re.findall(r'\$[0-9,.]+', text)
                    if len(salaries) > 0:
                        details['salary_min'] = re.sub(r'[\$,.]', '', salaries[0])
                        details['salary_max'] = re.sub(r'[\$,.]', '', salaries[1])
                        break

                if (text == "Compensation"):
                    compensation_found = True
                else:
                    description += text

            details['description'] = description

    
        except Exception as e:
            log("Error getting job details: {e}".format(e=e), "error")

    return details

    

def getJobs(query: str, job_ids: list[int]) -> list[dict]:
    """Get jobs from a given query"""
    query_url = "https://www.atlassian.com/company/careers/all-jobs?team=Engineering%2CDesign&location=United%20States&search={query}"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            result_lists = page.locator(".careers table").all()
            for result_list in result_lists:
                rows = result_list.locator('tr').all()
                for i in range(len(rows)):
                    if i == 0:
                        continue
                    anchor = rows[i].locator('a').all()
                    if anchor and len(anchor) > 0:
                        link = anchor[0].get_attribute('href')
                        id = link.replace('/company/careers/details/', '')
                        jobs_found += 1
                        if id not in job_ids:
                            jobs.append(id)

        except Exception as e:
            log(f"Error fetching jobs from Atlassian: {e}")

        finally:
            browser.close()

    return jobs, jobs_found

def getAtlassianJobs(job_ids: list[int]):
    log("Fetching jobs for Atlassian...")
    jobs = []
    found_ids = []
    total_jobs = 0
    queries = get_queries()

    for query in queries:
        job_results, jobs_found = getJobs(query, job_ids)
        total_jobs += jobs_found
        found_ids += job_results
        job_ids += job_results
        log("Number of new positions found for \"{query}\": {count}/{jobs_found}".format(query=query, count=len(job_results), jobs_found=jobs_found))

    for id in found_ids:
        jobDetails = getJobDetails(f'https://www.atlassian.com/company/careers/details/{id}', id)
        jobs.append(jobDetails)

    log("Total number of new positions found for Atlassian: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
