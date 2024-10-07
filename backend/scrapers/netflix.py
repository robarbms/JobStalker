from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from .utils import Extractor, log, queries
import time
import re
import json

"""
This function is used to get the job details from a given position element
"""
def getJobDetails(position: BeautifulSoup):
    details = {}
    try:
        title = position.find('h1', {'class': 'position-title'})
        if title:
            details['title'] = title.text

        location_container = position.find('p', {'class': 'position-location'})
        if location_container:
            details['location'] = location_container.find_all()[-1].text

        jd_container = position.find('div', {'class': 'custom-jd-container'})
        if jd_container:
            fields = jd_container.find_all('div', {'class': 'custom-jd-field'})
            for field in fields:
                type = field.find('h4').text
                content = field.find('div').text
                if " ID" in type:
                    details['job_id'] = content
                elif "Date" in type:
                    details['date_posted'] = content
                elif type == "Teams":
                    details['team'] = content
        else:
            return None

        description_container = position.find('div', {'class': 'position-job-description'})
        if description_container:
            description = ""
            lists = description_container.find_all('ul')
            for list in lists:
                if description != "":
                    description += " "
                description += list.get_text()

            details['description'] = description

        details['salary_min'] = 0
        details['salary_max'] = 0
        details['notes'] = ""
        details['summary'] = ""
        details['company'] = "Netflix"

    except Exception as e:
        log("Unable to parse job for Microsoft")
        log(str(e), "error")

    return details

"""
This function is used to get the job details for a given query
"""
def getJobs(query, job_ids):
    query_url = "https://explore.jobs.netflix.net/careers?query={query}&location=Seattle%2C%20WA%2C%20United%20States&sort_by=new"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as p:
        # Loading the browser and url to parse
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)

            cards = page.locator('div.card').all() # Get all job cards on the page
            position_container = page.locator('div.position-container') # Get the container for the selected job description

            # Parse JSON about the different job positions
            page_html = page.content()
            positions = re.search(r'"positions": ?\[( ?{[^\}]*"locations": ?\[[^\]]*[\}]*.*},?)*\]', page_html, re.MULTILINE | re.DOTALL)
            positions_json = "{" + positions.group(0) + "}"
            job_info = json.loads(positions_json)["positions"]

            for x in range(len(cards)): # skipping the first job as it's already been added to jobs
                cards[x].click() # Click the job card to select it and show it's description
                time.sleep(1) # Wait for the description to load

                # Get the job description and add it to the list of jobs
                html = position_container.inner_html()
                details = getJobDetails(BeautifulSoup(html, 'html.parser'))
                
                if details:
                    for pid in job_info:
                        if pid['display_job_id'] == details['job_id']:
                            details['link'] = pid['canonicalPositionUrl']
                            break

                    jobs.append(details)

        except Exception as e:
            log(f"Could not fetch results from Microsoft for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")

        finally:
            browser.close()

    return jobs

"""
Collects job postings from Netflix's careers page for a list of queries
"""
def getNetflixJobs(job_ids):
    log("Fetching jobs for Netflix...")
    base_url = "https://jobs.netflix.com/"
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
                    if (existing_job['job_id'] == job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

    log("Total number of positions found for Netflix: {count}".format(count=len(jobs)))
    return jobs
