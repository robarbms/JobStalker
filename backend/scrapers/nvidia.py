from playwright.sync_api import sync_playwright, Page, Locator
from .scraper_utils import log, get_queries
import time
import datetime

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
    # query_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q={query}&locations=91336993fab910af6d7169a81124c410&locations=91336993fab910af6d701e82d004c2c0&locations=16fc4607fc4310011e929f7115f90000&locations=d2088e737cbb01d5e2be9e52ce01926f&workerSubType=0c40f6bd1d8f10adf6dae161b1844a15&timeType=5509c0b5959810ac0029943377d47364"
    query_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q={query}&locations=91336993fab910af6d7169a81124c410&locations=91336993fab910af6d701e82d004c2c0&locations=16fc4607fc4310011e929f7115f90000&locations=d2088e737cbb01d5e2be9e52ce01926f&timeType=5509c0b5959810ac0029943377d47364"
    url = query_url.format(query=query)
    jobs = []

    with sync_playwright() as p:
        def get_links(page: Page, job_ids: list[str]):
            jobs_found = 0
            links = []
            result_list = page.locator('section[data-automation-id=jobResults] > ul > li').all()

            if result_list:
                jobs_found += len(result_list)
                for job_element in result_list:
                    job_id = job_element.locator('ul').text_content()
                    if job_id == None or job_id not in job_ids:
                        anchor = job_element.locator('a').all()
                        if anchor and len(anchor) > 0:
                            link = anchor[0].get_attribute('href')
                            links.append(link)
                
                # If there is a full page of results (20)
                # Check for a next button and click it.
                if jobs_found >= 20:
                    nav = page.locator('nav[aria-label=pagination] > div > ol + button')
                    if nav:
                        nav.click()
                        time.sleep(1)
                        more_links, more_jobs = get_links(page, job_ids)
                        links += more_links
                        jobs_found += more_jobs

            return links, jobs_found

        browser = p.chromium.launch()
        page = browser.new_page()
        jobs_found = 0

        try:
            page.goto(url)
            time.sleep(1)

            links, jobs_found = get_links(page, job_ids)

            for link in links:
                details = getJobDetails("https://nvidia.wd5.myworkdayjobs.com" + link, page)
                if 'job_id' in details and details['job_id'] not in job_ids:
                    jobs.append(details)

        except Exception as e:
            log(f"Could not fetch results from Nvidia for query \"{query}\"".format(query=query), "error")
            log(str(e), "error")

        finally:
            browser.close()

    return jobs, jobs_found

"""
    Gets jobs based on a list of queries
    Args:
    - job_ids: List of job IDs already in the database
"""
def getNvidiaJobs(job_ids: list[str]):
    log("Fetching jobs for Nvidia...")
    jobs = []
    total_jobs = 0
    queries = get_queries()

    for query in queries:
        job_results, jobs_found = getJobs(query, job_ids)
        total_jobs += jobs_found

        log("Number of new positions found for \"{query}\": {count}/{jobs_found}".format(query=query, count=len(job_results), jobs_found=jobs_found))
        job_ids += [job['job_id'] for job in job_results]
        jobs += job_results

        time.sleep(3)

    log("Total number of new positions found for Nvidia: {count}/{total_jobs}".format(count=len(jobs), total_jobs=total_jobs))
    return jobs
