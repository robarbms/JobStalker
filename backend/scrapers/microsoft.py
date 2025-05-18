from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
import re

def getJobDetails(job_number: str, page: Page):
    try:
        url = f"https://jobs.careers.microsoft.com/global/en/job/{job_number}".format(job_number=job_number)
        page.goto(url)
        time.sleep(2)
        h1 = page.locator("h1").all()
        title = h1[0].text_content().strip()
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
    except Exception as e:
        log(f"Could not fetch job from Microsoft for job number \"{job_number}\"".format(job_number=job_number), "error")
        log(str(e), "error")
        return None


def getJobs(query, job_ids):
    # query_url = "https://jobs.careers.microsoft.com/global/en/search?q={query}&lc=Bellevue%2C%20Washington%2C%20United%20States&lc=Redmond%2C%20Washington%2C%20United%20States&lc=Seattle%2C%20Washington%2C%20United%20States&p=Software%20Engineering&l=en_us&pg=1&pgSz=20&o=Recent&flt=true"
    query_url = "https://jobs.careers.microsoft.com/global/en/search?q={query}&lc=Bellevue%2C%20Washington%2C%20United%20States&lc=Redmond%2C%20Washington%2C%20United%20States&lc=Seattle%2C%20Washington%2C%20United%20States&l=en_us&pg=1&pgSz=20&o=Recent&flt=true"
    url = query_url.format(query=query)
    jobs = []
    jobs_found = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            time.sleep(5)

            main = page.locator("main")
            job_num_conts = main.locator('div[aria-label*="Job item"]').all()

            job_nums = []
            for job_num_cont in job_num_conts:
                job_nums.append(job_num_cont.get_attribute('aria-label').replace('Job item ', ''))

            jobs_found = len(job_nums)

            for job_num in job_nums:
                if job_num not in job_ids:
                    job_details = getJobDetails(job_num, page)
                    if job_details and job_details['date_posted'] != '':
                        jobs.append(job_details)


        except Exception as e:
            log(f"Could not fetch results from Microsoft for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")\
        
        finally:
            browser.close()

    return jobs, jobs_found

def getMicrosoftJobs(job_ids):
    log("Fetching jobs for Microsoft...")
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
                    if (job and 'job_id' in job and existing_job['job_id'] == job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

        time.sleep(1)

    log("Total number of new positions found for Microsoft: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs