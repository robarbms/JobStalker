from .board_scraper import greenhouse_jobs, scrape_jobs


def getMozillaJobs(job_ids, queries=None):
    return scrape_jobs("Mozilla", job_ids, queries, greenhouse_jobs, board="mozilla")
