from .board_scraper import greenhouse_jobs, scrape_jobs


def getToastJobs(job_ids, queries=None):
    return scrape_jobs("Toast", job_ids, queries, greenhouse_jobs, board="toast")
