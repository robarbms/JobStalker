from .board_scraper import rapid7_jobs, scrape_jobs


def getRapid7Jobs(job_ids, queries=None):
    return scrape_jobs("Rapid7", job_ids, queries, rapid7_jobs)
