from .board_scraper import mathworks_jobs, scrape_jobs


def getMathWorksJobs(job_ids, queries=None):
    return scrape_jobs("MathWorks", job_ids, queries, mathworks_jobs)
