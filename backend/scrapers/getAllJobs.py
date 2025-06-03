from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .microsoft import getMicrosoftJobs
from .nvidia import getNvidiaJobs
from .google import getGoogleJobs
from .amazon import getAmazonJobs
from .meta import getMetaJobs
from .adobe import getAdobeJobs
from .scraper_utils import log
from datetime import datetime
from .salesforce import getSalesforceJobs
from .zillow import getZillowJobs
from .atlassian import getAtlassianJobs

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
        'Amazon': getAmazonJobs,
        'Apple': getAppleJobs,
        'Google': getGoogleJobs,
        'Microsoft': getMicrosoftJobs,
        'Netflix': getNetflixJobs,
        'Nvidia': getNvidiaJobs,
        'Salesforce': getSalesforceJobs,
        'Zillow': getZillowJobs,
        'Atlassian': getAtlassianJobs,
    }

    # Cloudflare is blocking Adobe and Meta when scraping too often
    # Scraping 3 times daily ~5am, ~11am, ~5pm
    now = datetime.now()
    if (now.hour > 4 and now.hour <= 6) or (now.hour > 10 and now.hour <= 12) or (now.hour > 16 and now.hour <= 18):
        jobScrapers['Adobe'] = getAdobeJobs
        jobScrapers['Meta'] = getMetaJobs

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