from bs4 import BeautifulSoup
from .utils import queries
from playwright.sync_api import sync_playwright
import time

def getJobDetails(position):
    pass

def getAppleJobs():
    base_url = ""
    query_url = "https://jobs.apple.com/en-us/search?search={query}&sort=newest&location=seattle-SEA"

    queries = ["web", "engineer"]