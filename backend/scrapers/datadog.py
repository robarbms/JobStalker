from .board_scraper import greenhouse_jobs, scrape_jobs


def getDatadogJobs(job_ids, queries=None):
    return scrape_jobs("Datadog", job_ids, queries, greenhouse_jobs, board="datadog")
