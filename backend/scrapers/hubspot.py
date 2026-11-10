from .board_scraper import greenhouse_jobs, scrape_jobs


def getHubSpotJobs(job_ids, queries=None):
    return scrape_jobs("HubSpot", job_ids, queries, greenhouse_jobs, board="hubspotjobs")
