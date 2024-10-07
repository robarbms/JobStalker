from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .microsoft import getMicrosoftJobs
from .nvidia import getNvidiaJobs
from .google import getGoogleJobs
from .amazon import getAmazonJobs
from .meta import getMetaJobs
from .adobe import getAdobeJobs
from .utils import log
from datetime import datetime

def getAllJobs(job_ids):
    log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", None)
    log(f"Starting job search")
    jobs = []
    count = 0

    def getJobIds(company):
        if company in job_ids:
            return job_ids[company]
        return []
    
    jobs += getAmazonJobs(getJobIds('Amazon'))
    count += 1
    jobs += getGoogleJobs(getJobIds('Google'))
    count += 1
    jobs += getNvidiaJobs(getJobIds('Nvidia'))
    count += 1
    jobs += getAppleJobs(getJobIds('Apple'))
    count += 1
    jobs += getNetflixJobs(getJobIds('Netflix'))
    count += 1
    jobs += getMicrosoftJobs(getJobIds('Microsoft'))
    count += 1
    jobs += getAdobeJobs(getJobIds('Adobe'))
    count += 1
    jobs += getMetaJobs(getJobIds('Meta'))
    count += 1

    log(f"Found a total of {len(jobs)} unique jobs in {count} companies")
    log("Finished job search")

    return jobs