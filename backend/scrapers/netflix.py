from bs4 import BeautifulSoup
from .utils import queries
from playwright.sync_api import sync_playwright
import time

def getJobDetails(position):
    details = {}
    title = position.find('h1', {'class': 'position-title'})
    if title:
        details['title'] = title.text

    location_container = position.find('p', {'class': 'position-location'})
    if location_container:
        details['location'] = location_container.find_all()[-1].text

    jd_container = position.find('div', {'class': 'custom-jd-container'})
    fields = jd_container.find_all('div', {'class': 'custom-jd-field'})
    for field in fields:
        type = field.find('h4').text
        content = field.find('div').text
        if " ID" in type:
            details['id'] = content
        elif "Date" in type:
            details['date_posted'] = content
        elif type == "Teams":
            details['team'] = content

    description_container = position.find('div', {'class': 'position-job-description'})
    if description_container:
        description = ""
        lists = description_container.find_all('ul')
        for list in lists:
            if description != "":
                description += " "
            description += list.get_text()

        details['description'] = description

    return details

def getNetflixJobs():
    base_url = "https://jobs.netflix.com/"
    query_url = "https://explore.jobs.netflix.net/careers?query={query}&location=Seattle%2C%20WA%2C%20United%20States&sort_by=new"
    queries = ["frontend", "ux", "ui"]

    """
    for query in queries:
        url = query_url.format(query=query)
        soup = getPage(url)
    """
    url = query_url.format(query=queries[0])

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        jobs = []
        cards = page.locator('div.card').all()
        position_container = page.locator('div.position-container')
        jobs.append(getJobDetails(BeautifulSoup(position_container.inner_html(), 'html.parser')))

        for x in range(len(cards)):
            if x > 0:
                cards[x].click()
                time.sleep(1)
                html = position_container.inner_html()
                details = getJobDetails(BeautifulSoup(html, 'html.parser'))
                jobs.append(details)

        browser.close()  # Close the browser after scraping
        print(jobs)


    return "Netflix jobs processed."
