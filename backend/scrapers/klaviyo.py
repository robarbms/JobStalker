from .board_scraper import greenhouse_jobs, scrape_jobs


def getKlaviyoJobs(job_ids, queries=None):
    return scrape_jobs("Klaviyo", job_ids, queries, greenhouse_jobs, board="klaviyo")
