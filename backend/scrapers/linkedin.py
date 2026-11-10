from .board_scraper import linkedin_jobs, scrape_jobs


def getLinkedInJobs(job_ids, queries=None):
    return scrape_jobs("LinkedIn", job_ids, queries, linkedin_jobs)
