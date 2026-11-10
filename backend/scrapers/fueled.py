from .board_scraper import greenhouse_jobs, scrape_jobs


def getFueledJobs(job_ids, queries=None):
    return scrape_jobs("Fueled", job_ids, queries, greenhouse_jobs, board="fueledcareers")
