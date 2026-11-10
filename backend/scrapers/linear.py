from .board_scraper import ashby_jobs, scrape_jobs


def getLinearJobs(job_ids, queries=None):
    return scrape_jobs("Linear", job_ids, queries, ashby_jobs, board="linear")
