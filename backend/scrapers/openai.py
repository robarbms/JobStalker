from playwright.sync_api import sync_playwright, Page, Locator
from .utils import Extractor, log, queries, getPage
import time
import datetime
import re

# Not able to load the page with playwright
# Also won't work with requests
# Appears to be an issue of being blocked by Cloudflare
# Possibly need to use a library like https://github.com/lwthiker/curl-impersonate

def getJob(url: str, page: Page):
    try:
        pass
    except Exception as e:
        log("Error getting job", "error")

def getJobs(url: str, page: Page):
    pass

def getOpenAIJobs(job_ids: list[str]):
    cookies = {
        'ajs_anonymous_id': '99c31eff-85df-4ae4-b5fb-027f78fec314',
        'oai-did': '59518f70-c42f-483a-88ef-877f8ad0813d',
         'locale': 'en-US',
        'country': 'US',
        '_cfuvid': '4Y44Il9ch8vWVUQL5n.hO1phIMl8bmlZDi55.svMUbM-1727980472035-0.0.1.1-604800000',
         'consent': 'agreed',
         '_ga': 'GA1.1.1247525666.1727980472',
         '__stripe_mid': 'ea59e317-30a4-4e3b-bc64-a54d275426cfb2c1f2',
         '__cf_bm': 'kkKMpWK0qfgQIXVTPbJ8BLKBOCGy6H6UodSv0Y8b454-1727987985-1.0.1.1-mwlwNUGRx6BHRKBqCjKA4Horgi_GBol2W1xD40iWGIMvvDZQ0Tmuztb2OPJOjknEX1yVKZIykcVNyU_SOOAN4Q',
         'cf_clearance': 'sitJ90F3IdhsaXvuCkbJoJlkCviAlvv9VknRbh7eCTE-1727987986-1.2.1.1-x65w4CBhUCPvYeK7AXwwAY7GNsa6ThEQCJDOhLF4Qk5qK6pQqBc_ljpApIPmjUcPAXdqKvHkb8qwL0O8OfKGnQVsd3rTyvBCMaldY_TpdKxjvx5xyR9TBF8.Ui6TxaKkkntTXq1XOcyqhfz7J_xyPy8zaLE7cchdu2M7GI0Oyrg1H5lTWYTYq1FEAtmAMl3law0dbggyi9sAouBCeoBvLxvoTsBMJvQLmWFfr3Z4wyIGYiFWOEoistUKtLwbVJEmJc64mWCX5BpSeB8NNNl5AqX8Zkynpai6YezthBLP6BBsdtUJMsipC3r8658NYQs2L6rRR6C3WEnO8PKP2QJSV8u.LxCkakwA8fsK..xywjeySvp7gYPg3T1Kg3wtZxJL',
          '__stripe_sid': 'ff7c77a1-20aa-48ce-bd81-a1b618f0a6db03b633',
          '_ga_8MYC5SEFJ1': 'GS1.1.1727987985.2.1.1727988352.0.0.0'
    }
    log("Fetching jobs for OpenAI...")
    jobs = []
    url = "https://openai.com/careers/search/?l=seattle"


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url)
            time.sleep(3)
            title = page.title()
            print(page.title())

            job_container = page.locator('div.flex.flex-col')

            print(job_container, job_container.text_content())

            job_list = job_container.locator('div.w-full').all()

            print(len(job_list))

        except Exception as e:
            log("Error loading OpenAI careers page", "error")
            print(e)

    return jobs
