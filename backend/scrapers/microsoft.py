from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
import re

def getJobDetails(job_number: str, page: Page):
    try:
        url = f"https://apply.careers.microsoft.com/careers/job/{job_number}".format(job_number=job_number)
        # https://jobs.careers.microsoft.com/global/en/job/1970393556629426
        page.goto(url)
        time.sleep(2)
        title = page.locator('h2[class^="position-title-"]').text_content().strip()
        date_posted = ""
        location = ""

        detail_block = page.locator('div[class^="detailContainer-"]').all()

        for detail_item in detail_block:
            label = detail_item.locator('div[class^="detailLabel-"]')
            if label:
                value = detail_item.locator('div[class^="detailValue-"]').text_content().strip()
                label_text = label.text_content().strip()
                if label_text and value:
                    if label_text == 'Date posted':
                        date_posted = value
                    if label_text == 'Work site':
                        location = value

        job_description = page.locator("#job-description-container")
        job_description_paragraphs = job_description.locator("p").all()
        description = ""

        for desc in job_description_paragraphs:
            description += desc.text_content() + " "

        details = {
            "title": title,
            "job_id": job_number,
            "company": 'Microsoft',
            "link": url,
            "salary_min": 0,
            "salary_max": 0,
            "location": location,
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
    query_url = "https://apply.careers.microsoft.com/careers?query={query}&start=0&location=United+States&sort_by=timestamp&filter_include_remote=1&filter_work_site=0+days+%2F+week+in-office+%E2%80%93+remote"
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
            job_num_conts = main.locator('div[data-test-id="job-listing"]').all()
            # job_num_conts = main.locator('div[aria-label*="Job item"]').all()

            job_nums = []
            for job_num_cont in job_num_conts:
                anchor = job_num_cont.locator('a')
                link = anchor.get_attribute('href')
                job_id = link.replace('/careers/job/', '')
                job_nums.append(job_id)
                # job_nums.append(job_num_cont.get_attribute('aria-label').replace('Job item ', ''))

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