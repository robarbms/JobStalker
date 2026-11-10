from .board_scraper import greenhouse_jobs, scrape_jobs


def getSquareJobs(job_ids, queries=None):
    return scrape_jobs("Square", job_ids, queries, greenhouse_jobs, board="block", brand="Square")
