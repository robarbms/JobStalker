from .board_scraper import greenhouse_jobs, scrape_jobs


def getInterSystemsJobs(job_ids, queries=None):
    return scrape_jobs("InterSystems", job_ids, queries, greenhouse_jobs, board="intersystems")
