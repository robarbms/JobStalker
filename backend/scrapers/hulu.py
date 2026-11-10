from .board_scraper import hulu_jobs, scrape_jobs


def getHuluJobs(job_ids, queries=None):
    return scrape_jobs("Hulu", job_ids, queries, hulu_jobs)
