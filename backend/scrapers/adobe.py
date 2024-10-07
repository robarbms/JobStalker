from playwright.sync_api import sync_playwright, Page, Locator, Browser
from .utils import Extractor, log, queries
import time
import re

def getJobDescription(link: str):
    description = ""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(link)
        time.sleep(2)
        page.goto(link)
        time.sleep(2)

        try:
            description_elements = page.locator("div.jd-info p").all()
            for index in range(len(description_elements)):
                if index > 1:
                    description_text = description_elements[index].text_content().strip()
                    if len(description_text) > 0:
                        if description != "":
                            description+= "\n"
                        description += description_text

        except Exception as e:
            log(f"Error: {e}".format(e=e), "error")

        finally:
            browser.close()

    return description

def getJobs(query, job_ids):
    jobs = []
    query_url = "https://careers.adobe.com/us/en/search-results?keywords={query}"
    url = query_url.format(query=query)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(2)

            # set sort to recent
            selects = page.locator("select").all()
            selects[0].click()
            selects[0].select_option('Most recent')

            # Set city to Seattle
            city_select = page.locator("button[aria-controls=CityBody]")
            city_select.click()
            city_search = page.locator("input#facetInput_3")
            city_search.fill('seattle')
            time.sleep(1)
            seattle_select = page.locator("input[aria-label~=Seattle]")
            seattle_select.dispatch_event('click')
            time.sleep(2)

            job_list = page.locator("li.jobs-list-item").all()

            for job in job_list:
                details = {
                    "company": "Adobe",
                    "salary_min": 0,
                    "salary_max": 0,
                    "team": "",
                    "notes": "",
                    "summary": "",
                    "location": "Seattle, WA"
                }
                title_link = job.locator("span[role=heading] a")
                title = title_link.text_content().strip()
                details["title"] = title
                link = title_link.get_attribute("href")
                details["link"] = link
                job_id = job.locator("span.jobId span + i + span").text_content().strip()
                details["job_id"] = job_id
                posted_date = job.locator("span.job-postdate").text_content().strip()
                posted_date = re.sub("Posted Date[ \n]+", "", posted_date)
                details["date_posted"] = posted_date

                jobs.append(details)

        except Exception as e:
            log("Error fetching jobs: " + str(e), "error")
        finally:
            browser.close()
        
    for job in jobs:
        job['description'] = getJobDescription(job['link'])

    return jobs

def getAdobeJobs(job_ids):
    log("Fetching jobs for Adobe...")
    jobs = []

    for query in queries:
        job_results = getJobs(query, job_ids)
        log("Number of positions found for \"{query}\": {count}".format(query=query, count=len(job_results)))

        if(len(job_results) == 0):
            jobs = job_results
        else:
            for job in job_results:
                found = False
                for existing_job in jobs:
                    if(job and 'job_id' in job and existing_job and 'job_id' in existing_job and job['job_id'] == existing_job['job_id']):
                        found = True
                        break
                if (not found):
                    jobs.append(job)

    log("Total number of positions found: {count}".format(count=len(jobs)))
    return jobs