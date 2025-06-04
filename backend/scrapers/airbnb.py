from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
from datetime import datetime
import re

# Extracts the job id from a url string
def get_id(url_str):
    id = re.search(r"/\d+/", url_str)
    id = re.sub(r"/", "", id.group())
    return id

def getJobDetails(url: str):
    """Get job details from a given URL"""
    details = {
        'company': 'Airbnb',
        'job_id': get_id(url),
        'link': url,
        'salary_min': 0,
        'salary_max': 0,
        'notes': '',
        'summary': '',
        'location': 'Remote',
        'date_posted': datetime.now().strftime("%Y-%m-%d")
    }
    description = ""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            html = page.content()
            date_published = re.search(r'"datePublished":"[0-9\-]+', html)
            if date_published:
                date_str = date_published.group()
                date_str = re.sub('"datePublished":"', "", date_str)
                details["date_posted"] = date_str

            title = page.locator('h1').text_content().strip()
            if title:
                details['title'] = title

            info = page.locator('div.job-detail p, div.job-detail ul').all()
            for block in info:
                text = block.text_content()
                if text == "Your Location:":
                    break
                description += text
    
            details['description'] = description
        except Exception as e:
            log("Error getting job details: {e}".format(e=e), "error")

    return details

    

def getJobs(query: str, job_map: dict):
    """Get jobs from a given query"""
    query_url = "https://careers.airbnb.com/positions/?_search_input={query}&_offices=united-states&_workplace_type=live-and-work-anywhere&_jobs_sort=updated_at"
    url = query_url.format(query=query)
    job_links = []
    jobs = []
    jobs_found = 0
    
    def set_job(job_anchor, job_linksl, job_mapl):
        link_str = job_anchor.get_attribute("href")
        job_id = get_id(link_str)
        if job_id not in job_mapl:
            job_linksl.append(link_str)
            job_mapl[job_id] = True
        return job_linksl, job_mapl

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            links = page.locator("h3 a").all()
            jobs_found += len(links)
            for link in links:
                job_links, job_map = set_job(link, job_links, job_map)

            # Get how many pages of results there are
            page_count = 1
            pages = page.locator("div.facetwp-pager a").all()
            for page_link in pages:
                data_page = page_link.get_attribute("data-page")
                if data_page:
                    page_number = int(data_page)
                    if page_number > page_count:
                        page_count = page_number
            
            index = 2
            while index <= page_count:
                page.goto(url + "&_paged=" + str(index))
                time.sleep(2)
                links = page.locator("h3 a").all()
                jobs_found += len(links)
                for link in links:
                    job_links, job_map = set_job(link, job_links, job_map)
                index += 1

        except Exception as e:
            log(f"Error fetching jobs from Airbnb: {e}")

        finally:
            browser.close()

    return job_links, jobs_found, job_map

def getAirbnbJobs(job_ids: list[int]):
    log("Fetching jobs for Airbnb...")
    jobs = []
    job_links = []
    total_jobs = 0
    queries = get_queries()
    job_map = {}
    for id in job_ids:
        job_map[id] = True

    for query in queries:
        new_jobs, jobs_found, job_map = getJobs(query, job_map)
        total_jobs += jobs_found
        job_links += new_jobs

        log("Number of new positions found for \"{query}\": {count}/{jobs_found}".format(query=query, count=len(new_jobs), jobs_found=jobs_found))

    for link in job_links:
        jobDetails = getJobDetails(link)
        jobs.append(jobDetails)

    log("Total number of new positions found for Airbnb: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
