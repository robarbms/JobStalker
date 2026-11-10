from .board_scraper import ashby_jobs, scrape_jobs


def getAshbyJobs(job_ids, queries=None):
    return scrape_jobs("Ashby", job_ids, queries, ashby_jobs, board="ashby")
