from .board_scraper import greenhouse_jobs, scrape_jobs


def getCarGurusJobs(job_ids, queries=None):
    return scrape_jobs("CarGurus", job_ids, queries, greenhouse_jobs, board="cargurus")
