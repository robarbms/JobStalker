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
from .board_scraper import ScraperError
from .tiktok import getTikTokJobs
from .reddit import getRedditJobs
from .smartsheet import getSmartsheetJobs
from .github import getGitHubJobs
from .linkedin import getLinkedInJobs
from .uber import getUberJobs
from .doordash import getDoorDashJobs
from .oracle import getOracleJobs
from .serpapi import getSerpAPIJobs
from .duckduckgo import getDuckDuckGoJobs
from .mozilla import getMozillaJobs
from .square import getSquareJobs
from .shopify import getShopifyJobs
from .gitlab import getGitLabJobs
from .redfin import getRedfinJobs
from .hulu import getHuluJobs
from .zapier import getZapierJobs
from .spotify import getSpotifyJobs
from .pandora import getPandoraJobs

def getAllJobs(job_ids, queries):
    if queries is not None and not queries:
        return [], 0
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
        'TikTok': getTikTokJobs,
        'Reddit': getRedditJobs,
        'Smartsheet': getSmartsheetJobs,
        'GitHub': getGitHubJobs,
        'LinkedIn': getLinkedInJobs,
        'Uber': getUberJobs,
        'DoorDash': getDoorDashJobs,
        'Oracle': getOracleJobs,
        'SerpAPI': getSerpAPIJobs,
        'DuckDuckGo': getDuckDuckGoJobs,
        'Mozilla': getMozillaJobs,
        'Square': getSquareJobs,
        'Shopify': getShopifyJobs,
        'GitLab': getGitLabJobs,
        'Redfin': getRedfinJobs,
        'Hulu': getHuluJobs,
        'Zapier': getZapierJobs,
        'Spotify': getSpotifyJobs,
        'Pandora': getPandoraJobs,
        # 'Meta': getMetaJobs
    }

    # Cloudflare is blocking Adobe and Meta when scraping too often
    # Scraping 3 times daily ~5am, ~11am, ~5pm
    # now = datetime.now()
    # if (now.hour > 4 and now.hour <= 6) or (now.hour > 10 and now.hour <= 12) or (now.hour > 16 and now.hour <= 18):
    #     jobScrapers['Adobe'] = getAdobeJobs
    #     jobScrapers['Meta'] = getMetaJobs

    num_scrapers = len(jobScrapers)

    print(f">>>>>> Scraping {len(jobScrapers)} companies for queries: {queries}")
    for company, scraper in jobScrapers.items():
        ids = getJobIds(company)
        try:
            new_jobs, found = scraper(ids, queries)
        except ScraperError as error:
            log(f"Error fetching jobs for {company}: {error}", "error")
            continue
        found_count += found
        jobs += new_jobs
        log(f"{len(new_jobs)}/{found}", None)

    log(f">>>>>> Found a total of {len(jobs)}/{found_count} new jobs in {len(jobScrapers)} companies")

    return jobs, found_count