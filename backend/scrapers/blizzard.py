from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
import datetime

# Extracts job details from a Blizzard job posting
def getJobDetails(details, page: Page):
    url = details['link']
    description = ""

    try:
        page.goto(url)
        time.sleep(1)

        content = page.locator('div.jd-info > div').all()
        for paragraph in content:
            description += paragraph.text_content().strip() + " "

        details['description'] = description

    except Exception as e:
        log(e, "error")
    
    finally:
        return details


def get_links(page: Page, job_ids: list[str]):
    jobs_found = 0
    links = []

    job_listings = page.locator("li.jobs-list-item").all()
    jobs_found += len(job_listings)

    index = 0
    for job_listing in job_listings:
        index += 1
        data = {
            'company': 'Blizzard',
            'salary_min': 0,
            'salary_max': 0,
            'notes': '',
            'summary': '',
            'location': ''
        }
        try:
            is_usa = False
            location = job_listing.locator("span.job-location span").all()
            if location and len(location) > 1:
                location = location[1].text_content()
                print(location)
                if "United States" in location:
                    is_usa = True
                    data['location'] = location
            else:
                is_usa = True

            if is_usa == True:
                job_id = job_listing.locator("span.jobId span").all()
                if len(job_id) > 1:
                    job_id = job_id[1].text_content()

                if job_id not in job_ids:
                    data['job_id'] = job_id

                    title = job_listing.locator("div.job-title span").text_content().strip()
                    data['title'] = title

                    date_posted = job_listing.locator("span.job-postdate").text_content().strip()
                    date_posted = date_posted.replace("Posted Date", "").strip()
                    data['date_posted'] = date_posted

                    anchor = job_listing.locator('a')
                    if anchor:
                        link = anchor.get_attribute('href')
                        data['link'] = link
                        links.append(data)

        except Exception as e:
            log(f"Could not parse job listing number {index}")
            print(e)
    

    return links, jobs_found

def getJobs(query: str, job_ids: list[str]):
    query_url="https://careers.blizzard.com/global/en/search-results?keywords={query}"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_default_timeout(6000)
        jobs_found = 0

        try:
            page.goto(url)
            time.sleep(3)


        except Exception as e:
            log(f"Could not fetch results from Blizzard for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")


        links, jobs_found = get_links(page, job_ids)

        for link in links:
            details = getJobDetails(link, page)
            jobs.append(details)

        browser.close()

    return jobs, jobs_found

"""
    Gets jobs based on a list of queries
    Args:
    - job_ids: List of job IDs already in the database
"""
def getBlizzardJobs(job_ids: list[str], queries):
    log("Fetching jobs for Blizzard...", "info", no_end=True)
    jobs = []
    total_jobs = 0
    if queries == None:
        queries = get_queries()

    for query in queries:
        job_results, jobs_found = getJobs(query, job_ids)
        total_jobs += jobs_found

        job_ids += [job['job_id'] for job in job_results]
        jobs += job_results

        time.sleep(3)

    return jobs, jobs_found
