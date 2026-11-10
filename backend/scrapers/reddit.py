from .board_scraper import greenhouse_jobs, scrape_jobs


def getRedditJobs(job_ids, queries=None):
    return scrape_jobs("Reddit", job_ids, queries, greenhouse_jobs, board="reddit")
