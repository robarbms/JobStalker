from playwright.sync_api import sync_playwright, Page, Locator
from .utils import log, stringToDateStamp
import time
from datetime import datetime
import re


def getJobs(job_ids: list[int]) -> list[dict]:
    url = f"https://zillow.wd5.myworkdayjobs.com/Zillow_Group_External?locations=76d84517207210c0ae0423975342e5e5&locations=76d84517207210c0ae04392fff1ae612&locations=bf3166a9227a01f8b514f0b00b147bc9&timeType=156fb9a2f01c10be203b6e91581a01d1&workerSubType=156fb9a2f01c10bed80e140d011a9559"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        # Finds all the jobs on the page
        # If there are more pages, will click the next
        #   page and repeat until there are no more pages
        def get_jobs_from_page(job_ids, page) -> list[dict]:
            jobs = []
            jobs_found = 0
            lists = page.locator("ul[role=list]").all()

            if len(lists) == 0:
                log("Unable to connect to Zillow.", "error")

            else:
                for list in lists:
                    aria_label = list.get_attribute("aria-label")
                    if aria_label:

                        # Finds the job listings list
                        if re.search(r'^Page', aria_label):
                            result_list = list.locator("> li").all()
                            jobs_found = len(result_list)

                            # Loop through each job and add it to the jobs[] list
                            for item in result_list:
                                details = {
                                    "company": "Zillow",
                                    'salary_min': 0,
                                    'salary_max': 0,
                                    'notes': '',
                                    'summary': '',
                                    'location': 'Seattle, WA',
                                }
                                children = item.locator("> div").all()

                                try:
                                    for index in range(len(children)):
                                        child = children[index]
                                        if index == 0:
                                            h3 = child.locator("h3")
                                            link = h3.locator("a")
                                            details['title'] = h3.text_content()
                                            details['link'] = "https://zillow.wd5.myworkdayjobs.com/" + link.get_attribute("href")
                                        elif index < len(children):
                                            content = child.locator("dd").text_content()

                                            if re.search(r'Posted', content):
                                                posted = stringToDateStamp(content)
                                                details['date_posted'] = posted
                                            else:
                                                details['location'] = content
                                    
                                    job_id = item.locator("ul li").text_content()

                                except Exception as e:
                                    log(f"Error parsing job details: {e}", "error")

                                if job_id and job_id not in job_ids:
                                    details['job_id'] = job_id
                                    try:
                                        link.click()
                                        time.sleep(1)
                                        description = page.locator("div[data-automation-id=jobPostingDescription]")
                                        if description:
                                            description = description.text_content()
                                            details['description'] = description
                                    except Exception as e:
                                        log(f"Error parsing job description: {e}", "error")

                                    jobs.append(details)

                            # Check if there is a next page
                            page_info = re.match(r'Page (\d+) of (\d+)', aria_label)
                            if page_info:
                                # Figure out the current and total number of pages
                                current_page = int(page_info.group(1))
                                total_pages = int(page_info.group(2))
                                if current_page < total_pages:
                                    pagination = page.locator("ol > li > button").all()
                                    if pagination and len(pagination) > 0:
                                        for pagen in pagination:
                                            page_al = pagen.get_attribute("aria-label")
                                            if page_al == f"page {current_page + 1}":
                                                # Click on the next page button and repeat the process
                                                pagen.click()
                                                time.sleep(1)
                                                more_jobs, more_jobs_found = get_jobs_from_page(job_ids, page)
                                                jobs += more_jobs
                                                jobs_found += more_jobs_found
            return jobs, jobs_found

        try:
            page.goto(url)
            time.sleep(2) # Wait for the page to load

            return get_jobs_from_page(job_ids, page)

        except Exception as e:
            log(f"Error fetching jobs from Zillow: {e}")

        finally:
            browser.close()

def getZillowJobs(job_ids: list[int]):
    log("Fetching jobs for Zillow...")

    jobs, total_jobs = getJobs(job_ids)
    log("Total number of new positions found for Zillow: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
