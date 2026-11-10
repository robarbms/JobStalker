from .board_scraper import greenhouse_jobs, scrape_jobs


def getCanonicalJobs(job_ids, queries=None):
    return scrape_jobs("Canonical", job_ids, queries, greenhouse_jobs, board="canonical")
