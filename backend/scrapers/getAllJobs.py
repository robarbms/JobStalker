from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .microsoft import getMicrosoftJobs
from .nvidia import getNvidiaJobs
from .google import getGoogleJobs
from .utils import log
from datetime import datetime

def getAllJobs(job_ids):
    log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", None)
    log(f"Starting job search")
    jobs = []
    count = 0

    googleJobs = job_ids['Google'] if 'Google' in job_ids else []

    jobs += getGoogleJobs(googleJobs)
    count += 1
    jobs += getNvidiaJobs(job_ids['Nvidia'])
    count += 1
    jobs += getAppleJobs(job_ids['Apple'])
    count += 1
    jobs += getNetflixJobs(job_ids['Netflix'])
    count += 1
    jobs += getMicrosoftJobs(job_ids['Microsoft'])
    count += 1

    log(f"Found a total of {len(jobs)} unique jobs in {count} companies")
    log("Finished job search")

    return jobs