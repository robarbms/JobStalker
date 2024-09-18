from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .utils import log
from datetime import datetime

def getAllJobs():
    log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", None)
    log(f"Starting job search")
    jobs = []
    count = 0

    jobs += getAppleJobs()
    count += 1
    jobs += getNetflixJobs()
    count += 1

    log(f"Found a total of {len(jobs)} unique jobs in {count} companies")
    log("Finished job search")

    return jobs