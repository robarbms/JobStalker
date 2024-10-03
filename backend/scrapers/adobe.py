from playwright.sync_api import sync_playwright, Page
from .utils import Extractor, log, queries
import time
import re

def getJobDetails():
    pass

def getJobs(query, job_ids):
    jobs = []

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