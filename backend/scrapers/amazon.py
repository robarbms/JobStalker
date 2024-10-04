from playwright.sync_api import sync_playwright, Page, Browser
from .utils import Extractor, log, queries
import time
import re

def getJobDetails(url: str, browser: Browser):
    description = ""
    location = ""
    team = ""
    page = browser.new_page()
    
    try:
        page.goto(url)
        content_container = page.locator('div#job-detail-body > div').all()
        if len(content_container) > 0:
            content_container = content_container[0]
            description = content_container.inner_text()

        side_bar_row = page.locator('div.sidebar div.row').all()
        if len(side_bar_row) > 0:
            job_details = side_bar_row[0]
            detail_elements = job_details.locator('> ul > li').all()
            if len(detail_elements) > 1: # assuming there are at least two elements in the list for location and team
                location = detail_elements[0].inner_text()
                team = detail_elements[1].inner_text()

    except Exception as e:
        log("Failed to get description: {error}".format(error=e), "error")

    finally:
        page.close()

    return description, location, team

def getJobs(query: str):
    jobs = []
    query_url = "https://www.amazon.jobs/en/search?offset=0&result_limit=10&sort=recent&distanceType=Mi&radius=24km&latitude=&longitude=&loc_group_id=&loc_query=Washington%2C%20United%20States&base_query={query}&city=&country=USA&region=Washington&county=&query_options=&"
    url = query_url.format(query=query)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(1)

            job_tiles = page.locator('div.job').all()

            for tile in job_tiles:
                title_h3 = tile.locator('h3')
                title = title_h3.text_content().strip()
                anchor = title_h3.locator('a')
                link = 'https://www.amazon.jobs' + anchor.get_attribute('href')
                job_id = re.search(r'/jobs/(\d+)/', link).group(1)
                posted = tile.locator('h2.posting-date')
                date_posted = posted.text_content().strip().replace('Posted ', '')
                description, location, team = getJobDetails(link, browser)
                details = {
                    'job_id': job_id,
                    'title': title,
                    'link': link,
                    'date_posted': date_posted,
                    'company': 'Amazon',
                    'salary_min': 0,
                    'salary_max': 0,
                    'notes': '',
                    'summary': '',
                    'description': description,
                    'location': location,
                    'team': team,
                }
                jobs.append(details)


        except Exception as e:
            log("Error loading page: {error}".format(error=e), "error")

        finally:
            browser.close()

    return jobs

def getAmazonJobs(job_ids: list[str]):
    log("Fetching jobs for Amazon...")
    jobs = []

    for query in queries:
        job_results = getJobs(query)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if (len(jobs) == 0):
            jobs = job_results
        else:
            for job in job_results:
                found = False
                for existing_job in jobs:
                    if existing_job['job_id'] == job['job_id']:
                        found = True
                        break
                if not found:
                    jobs.append(job)

    log("Total number of positions found: {count}".format(count=len(jobs)))

    return jobs