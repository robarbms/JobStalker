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
from .atlassian import getAtlassianJobs
from .expedia import getExpediaJobs
from .airbnb import getAirbnbJobs
from .blizzard import getBlizzardJobs

def getAllJobs(job_ids, queries):
    jobs = []
    found_count = 0

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
        # 'Salesforce': getSalesforceJobs,
        'Atlassian': getAtlassianJobs,
        'Expedia': getExpediaJobs,
        'Airbnb': getAirbnbJobs,
        'Blizzard': getBlizzardJobs,
        'Adobe': getAdobeJobs,
        # 'Meta': getMetaJobs
    }

    # Cloudflare is blocking Adobe and Meta when scraping too often
    # Scraping 3 times daily ~5am, ~11am, ~5pm
    # now = datetime.now()
    # if (now.hour > 4 and now.hour <= 6) or (now.hour > 10 and now.hour <= 12) or (now.hour > 16 and now.hour <= 18):
    #     jobScrapers['Adobe'] = getAdobeJobs
    #     jobScrapers['Meta'] = getMetaJobs

    num_scrapers = len(jobScrapers)

    print(f">>>>>> Scraping {len(jobScrapers)} companies for the query: '{queries[0]}'")
    for company, scraper in jobScrapers.items():
        ids = getJobIds(company)
        new_jobs, found = scraper(ids, queries)
        found_count += found
        jobs += new_jobs
        log(f"{len(new_jobs)}/{found}", None)

    log(f">>>>>> Found a total of {len(jobs)}/{found_count} new jobs in {len(jobScrapers)} companies")

    return jobs, found_count