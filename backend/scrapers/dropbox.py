from .board_scraper import greenhouse_jobs, scrape_jobs


def getDropboxJobs(job_ids, queries=None):
    return scrape_jobs("Dropbox", job_ids, queries, greenhouse_jobs, board="dropbox")
