from .apple import getAppleJobs
from .netflix import getNetflixJobs
from .microsoft import getMicrosoftJobs
from .nvidia import getNvidiaJobs
from .google import getGoogleJobs
from .amazon import getAmazonJobs
from .meta import getMetaJobs
from .adobe import getAdobeJobs
from .scraper_utils import get_queries, log
from .salesforce import getSalesforceJobs
from .atlassian import getAtlassianJobs
from .expedia import getExpediaJobs
from .airbnb import getAirbnbJobs
from .blizzard import getBlizzardJobs
from .board_scraper import ScraperError
from .company_locations import filter_company_jobs
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
from .mathworks import getMathWorksJobs
from .akamai import getAkamaiJobs
from .intersystems import getInterSystemsJobs
from .cargurus import getCarGurusJobs
from .athenahealth import getAthenahealthJobs
from .bose import getBoseJobs
from .hubspot import getHubSpotJobs
from .toast import getToastJobs
from .klaviyo import getKlaviyoJobs
from .datadog import getDatadogJobs
from .rapid7 import getRapid7Jobs
from .dropbox import getDropboxJobs
from .grafana import getGrafanaJobs
from .automattic import getAutomatticJobs
from .buffer import getBufferJobs
from .tailscale import getTailscaleJobs
from .helpscout import getHelpScoutJobs
from .signals37 import get37signalsJobs
from .supabase import getSupabaseJobs
from .ashby import getAshbyJobs
from .close import getCloseJobs
from .customerio import getCustomerIOJobs
from .linear import getLinearJobs
from .webflow import getWebflowJobs
from .sourcegraph import getSourcegraphJobs
from .fueled import getFueledJobs
from .canonical import getCanonicalJobs
from .posthog import getPostHogJobs
from .zillow import getZillowJobs

def get_scrapers():
    return {
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
        'MathWorks': getMathWorksJobs,
        'Akamai Technologies': getAkamaiJobs,
        'InterSystems': getInterSystemsJobs,
        'CarGurus': getCarGurusJobs,
        'athenahealth': getAthenahealthJobs,
        'Bose': getBoseJobs,
        'HubSpot': getHubSpotJobs,
        'Toast': getToastJobs,
        'Klaviyo': getKlaviyoJobs,
        'Datadog': getDatadogJobs,
        'Rapid7': getRapid7Jobs,
        'Dropbox': getDropboxJobs,
        'Grafana Labs': getGrafanaJobs,
        'Automattic': getAutomatticJobs,
        'Buffer': getBufferJobs,
        'Tailscale': getTailscaleJobs,
        'Help Scout': getHelpScoutJobs,
        '37signals': get37signalsJobs,
        'Supabase': getSupabaseJobs,
        'Ashby': getAshbyJobs,
        'Close': getCloseJobs,
        'Customer.io': getCustomerIOJobs,
        'Linear': getLinearJobs,
        'Webflow': getWebflowJobs,
        'Sourcegraph': getSourcegraphJobs,
        'Fueled': getFueledJobs,
        'Canonical': getCanonicalJobs,
        'PostHog': getPostHogJobs,
        'Zillow': getZillowJobs,
        # 'Meta': getMetaJobs
    }

def getAllJobs(job_ids, queries, companies=None, max_jobs=None, errors=None):
    queries = get_queries() if queries is None else queries
    if not queries:
        return [], 0
    if max_jobs is not None and (type(max_jobs) is not int or max_jobs < 1):
        raise ValueError("max_jobs must be a positive whole number.")
    scrapers = get_scrapers()
    selected = list(scrapers) if companies is None else companies
    if any(company not in scrapers for company in selected):
        raise ValueError("An unavailable company was selected.")
    jobs = []
    found_count = 0

    print(f">>>>>> Scraping {len(selected)} companies for queries: {queries}")
    for company in selected:
        scraper = scrapers[company]
        ids = list(job_ids.get(company, []))
        try:
            if company == "Zillow":
                new_jobs, found = scraper(ids)
                new_jobs = [
                    job for job in new_jobs
                    if any(query.strip().casefold() in job.get("title", "").casefold() for query in queries)
                ]
            else:
                new_jobs, found = scraper(ids, queries)
        except ScraperError as error:
            log(f"Error fetching jobs for {company}: {error}", "error")
            if errors is not None:
                errors.append(f"{company}: {error}")
            continue
        new_jobs = filter_company_jobs(new_jobs, company)
        unique_jobs = []
        seen = {str(job_id) for job_id in job_ids.get(company, [])}
        for job in new_jobs:
            key = str(job["job_id"])
            if key not in seen:
                unique_jobs.append(job)
                seen.add(key)
        new_jobs = unique_jobs[:max_jobs] if max_jobs is not None else unique_jobs
        found_count += found
        jobs += new_jobs
        log(f"{len(new_jobs)}/{found}", None)

    log(f">>>>>> Found a total of {len(jobs)}/{found_count} new jobs in {len(selected)} companies")

    return jobs, found_count