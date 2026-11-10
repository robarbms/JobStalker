from .board_scraper import ashby_jobs, scrape_jobs


def getCloseJobs(job_ids, queries=None):
    return scrape_jobs("Close", job_ids, queries, ashby_jobs, board="close")
