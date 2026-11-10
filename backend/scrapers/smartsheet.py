from .board_scraper import greenhouse_jobs, scrape_jobs


def getSmartsheetJobs(job_ids, queries=None):
    return scrape_jobs("Smartsheet", job_ids, queries, greenhouse_jobs, board="smartsheet")
