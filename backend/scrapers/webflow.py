from .board_scraper import ashby_jobs, scrape_jobs


def getWebflowJobs(job_ids, queries=None):
    return scrape_jobs("Webflow", job_ids, queries, ashby_jobs, board="webflow")
