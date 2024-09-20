from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .microsoft import getMicrosoftJobs
from .utils import log
from datetime import datetime

def getAllJobs(job_ids):
    log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", None)
    log(f"Starting job search")
    jobs = []
    count = 0

    jobs += getAppleJobs(job_ids['Apple'])
    count += 1
    jobs += getNetflixJobs(job_ids['Netflix'])
    count += 1
    jobs += getMicrosoftJobs(job_ids['Microsoft'])
    count += 1

    log(f"Found a total of {len(jobs)} unique jobs in {count} companies")
    log("Finished job search")

    return jobs