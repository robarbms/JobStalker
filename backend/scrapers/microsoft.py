from playwright.sync_api import sync_playwright, Page, Locator
from .utils import log, queries
import time
import re

def getJobDetails(job_number: str, page: Page):
    url = f"https://jobs.careers.microsoft.com/global/en/job/{job_number}".format(job_number=job_number)
    page.goto(url)
    time.sleep(2)
    title = page.locator("h1").text_content().strip()
    p_tags = page.locator("p").all()
    date_posted = ""
    team = ""
    group = page.get_by_role("group")
    stacks = group.locator("div.ms-Stack").all()
    for idx in range(len(stacks)):
        if stacks[idx].text_content().strip().startswith("Date posted") and date_posted == "":
            date_posted = stacks[idx].text_content().replace("Date posted", "").strip()    
        if stacks[idx].text_content().strip().startswith("Discipline") and idx < len(stacks) - 1:
            team = stacks[idx + 1].text_content().strip()

    after_hr = page.locator("hr + div").all()
    description = after_hr[1].text_content()

    details = {
        "title": title,
        "job_id": job_number,
        "company": 'Microsoft',
        "link": url,
        "salary_min": 0,
        "salary_max": 0,
        "location": p_tags[0].text_content(),
        "date_posted": date_posted,
        "team": "",
        "description": description,
        "notes": "",
        "summary": ""
    }

    return details


def getJobs(query, job_ids):
    query_url = "https://jobs.careers.microsoft.com/global/en/search?q={query}&lc=Bellevue%2C%20Washington%2C%20United%20States&lc=Redmond%2C%20Washington%2C%20United%20States&lc=Seattle%2C%20Washington%2C%20United%20States&p=Software%20Engineering&l=en_us&pg=1&pgSz=20&o=Recent&flt=true"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)

        main = page.locator("main")
        job_num_conts = main.locator('div[aria-label*="Job item"]').all()

        job_nums = []
        for job_num_cont in job_num_conts:
            job_nums.append(job_num_cont.get_attribute('aria-label').replace('Job item ', ''))

        for job_num in job_nums:
            if job_num not in job_ids:
                job_details = getJobDetails(job_num, page)
                if job_details['date_posted'] != '':
                    jobs.append(job_details)

        browser.close()
        return jobs


        

def getMicrosoftJobs(job_ids):
    log("Fetching jobs for Microsoft...")
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
                    if (job and 'job_id' in job and existing_job['job_id'] == job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

        time.sleep(1)

    log("Total number of positions found: {count}".format(count=len(jobs)))
    return jobs