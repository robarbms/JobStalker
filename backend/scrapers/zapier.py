from .board_scraper import ashby_jobs, scrape_jobs


def getZapierJobs(job_ids, queries=None):
    return scrape_jobs("Zapier", job_ids, queries, ashby_jobs, board="zapier")
