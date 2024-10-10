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
    
    jobScrapers = {
        'Adobe': getAdobeJobs,
        'Amazon': getAmazonJobs,
        'Apple': getAppleJobs,
        'Google': getGoogleJobs,
        'Meta': getMetaJobs,
        'Microsoft': getMicrosoftJobs,
        'Netflix': getNetflixJobs,
        'Nvidia': getNvidiaJobs,
    }

    num_scrapers = len(jobScrapers)

    for company, scraper in jobScrapers.items():
        count += 1
        print(f">>>>>> {company} scraping {count}/{num_scrapers}")
        ids = getJobIds(company)
        new_jobs = scraper(ids)
        print(f">>>>>> Found {len(new_jobs)} new jobs for {company}")
        jobs += new_jobs

    log(f">>>>>> Found a total of {len(jobs)} unique jobs in {count} companies")
    log("Finished job search")

    return jobs