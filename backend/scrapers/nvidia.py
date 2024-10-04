from playwright.sync_api import sync_playwright, Page, Locator
from .utils import Extractor, log, queries
import time
import datetime
import re

# Converts a date string (e.g., "Posted 2 Days Ago") to a datetime object
def getDate(date_str):
    date_str = date_str.replace("Posted ", "")
    date_str = date_str.replace(" Ago", "")
    date = datetime.datetime.now()

    if "Today" not in date_str:
        if "Yesterday" in date_str:
            date = date - datetime.timedelta(days=1)
        else:
            parts = date_str.split(" ")
            if len(parts) >= 2:
                amount = int(parts[0].replace("+", ""))
                unit = parts[1]
                if unit == "Days" or unit == "Day":
                    date = date - datetime.timedelta(days=amount)
                elif unit == "Weeks" or unit == "Week":
                    date = date - datetime.timedelta(days=amount*7)
                elif unit == "Months" or unit == "Month":
                    date = date - datetime.timedelta(days=amount*30)

    return date.strftime("%Y-%m-%d")

# Extracts job details from a Nvidia job posting
def getJobDetails(url: str, page: Page):
    details = {
        'link': url,
        'company': 'Nvidia',
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
    }
    try:
        page.goto(url)
        time.sleep(1)
        title = page.locator('h2').all()[0].text_content()
        if title:
            details['title'] = title

        def_lists = page.locator('dl').all()

        for deff in def_lists:
            key = deff.locator('dt').text_content().strip()
            value = deff.locator('dd').all()
            value = " ".join([v.text_content().strip() if type(v) is Locator else v for v in value])

            if key and value:
                if key == 'locations':
                    details['location'] = value
                elif key == 'posted on':
                    details['date_posted'] = getDate(value)
                elif key == 'job requisition id':
                    details['job_id'] = value

        description = page.locator('div[data-automation-id=jobPostingDescription]')
        if description:
            description = description.text_content().strip()
            details['description'] = description

    except Exception as e:
        log(e, "error")
    
    finally:
        return details

def getJobs(query: str, job_ids: list[str]):
    query_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q={query}&locations=91336993fab910af6d716528e9d4c406&locations=d2088e737cbb01d5e2be9e52ce01926f&locations=16fc4607fc4310011e929f7115f90000&locations=91336993fab910af6d701e82d004c2c0"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(1)

            result_list = page.locator('section[data-automation-id=jobResults] ul')

            if result_list:
                job_elements = result_list.locator('li a').all()

                if job_elements and len(job_elements) > 0:
                    links = [element.get_attribute('href') for element in job_elements]

                    for link in links:
                        details = getJobDetails("https://nvidia.wd5.myworkdayjobs.com" + link, page)
                        jobs.append(details)

        except Exception as e:
            log(f"Could not fetch results from Nvidia for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")

        finally:
            browser.close()

    return jobs

"""
    Gets jobs based on a list of queries
    Args:
    - job_ids: List of job IDs already in the database
"""
def getNvidiaJobs(job_ids: list[str]):
    log("Fetching jobs for Nvidia...")
    jobs = []

    for query in queries:
        job_results = getJobs(query, job_ids)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if(len(job_results) == 0):
            jobs = job_results
        else:
            for job in job_results:
                if 'job_id' not in job:
                    log("Missing jobid for job: {job}".format(job=job), "error")
                else:
                    found = False
                    for existing_job in jobs:
                        if(job['job_id'] == existing_job['job_id']):
                            found = True
                            break
                    if (not found):
                        jobs.append(job)

    log("Total number of positions found: {count}".format(count=len(jobs)))
    return jobs
