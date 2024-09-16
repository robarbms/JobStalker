from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, Page
from datetime import datetime

"""
    Gets the contents of a page and returns it as a soup object
"""
def getPage(url):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    print("Getting page for {0}...".format(url))
    response = requests.get(url, headers=request_headers)
    if response.status_code == 200:
        print("Page successfully downloaded.")
        html_doc = response.text
        print("Received {0} bytes.".format(len(html_doc)))
        print("Parsing page...")
        soup = BeautifulSoup(html_doc, 'html.parser')
        print("Page sucessfully parsed. Returning as a soup object.")
        return soup
    else:
        msg = "Error: {0}. Unable to get page content for {1}".format(response.status_code, url)
        print(msg)
        return {
            'error': msg
        }

class Extractor:
    def __init__(self, page: Page, company: str, job_id: str):
        self.page = page
        self.company = company
        self.job_id = job_id
    
    def getText(self, selector: str, required=True) -> str:
        if self.page.query_selector(selector):
            return self.page.locator(selector).text_content().strip()
        else:
            if required:
                log("Missing required field '{0}' for company {1} and job id {2}".format(selector, self.company, self.job_id), level="error")
            return ""

def log(message: str, level="info"):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("{0} [{1}]: {2}".format(ct, level.upper(), message))

queries = [
    "frontend",
    "ui",
    "ux",
]