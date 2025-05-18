from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, Page
from datetime import datetime, timedelta
import re
import configparser
import os

"""
    Gets the contents of a page and returns it as a soup object
"""
def getPage(url, cookies=None):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    }

    print("Getting page for {0}...".format(url))
    response = requests.get(url, headers=request_headers, cookies=cookies)
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
    
    def getText(self, selector: str, required=False) -> str:
        if self.page.query_selector(selector):
            return self.page.locator(selector).text_content().strip()
        else:
            if required:
                log("Missing required field '{0}' for company {1} and job id {2}".format(selector, self.company, self.job_id), level="error")
            return ""

def log(message: str, level="info"):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fd = datetime.now().strftime("%Y-%m-%d")
    log_file = "logs/{0}.log".format(fd)
    error_file = "logs/errors/{0}.log".format(fd)

    log_msg = message
    if level != None:
        log_msg = "[{0}] {1}: {2}".format(level.upper(), ct, message)

    with open(log_file, "a") as f:
        f.write(log_msg + "\n")

    if level == "error":
        with open(error_file, "a") as f:
            f.write(log_msg + "\n")
        
    print(log_msg)

def get_queries():
    config = configparser.ConfigParser()
    cur_path = os.path.realpath(__file__)
    root_path = re.sub(r'JobStalker.*', 'JobStalker', cur_path)
    config_path = root_path + '\\config.ini'
    config.read(config_path)
    scenario = config.get('app', 'scenario')
    queries = config.get('scrapers', 'webdev_queries')
    if scenario:
        scenario_queries = config.get('scrapers', f"{scenario}_queries")
        if scenario_queries:
            queries = scenario_queries
    queries = queries.split(',')
    return queries

def stringToDateStamp(date_str: str) -> str:
    date_str = date_str.strip().lower()
    now = datetime.now()
    if re.search(r"today", date_str):
        return now.strftime("%Y-%m-%d")
    if re.search(r"yesterday", date_str):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if re.search(r"ago", date_str):
        try:
            date_parts = re.match(r'posted (\d+)\+? (day|week|month|year)s? ago', date_str)
            date_parts= date_parts.groups()
            num = int(date_parts[0])
            unit = date_parts[1]
        except Exception as e:
            log("Error parsing date string: {0}".format(e), "error")
        if unit == "day":
            return (now - timedelta(days=num)).strftime("%Y-%m-%d")
        elif unit == "week":
            return (now - timedelta(weeks=num)).strftime("%Y-%m-%d")
        elif unit == "month":
            return (now - timedelta(months=num)).strftime("%Y-%m-%d")
        elif unit == "year":
            return (now - timedelta(years=num)).strftime("%Y-%m-%d")
