from .board_scraper import greenhouse_jobs, scrape_jobs


def getAutomatticJobs(job_ids, queries=None):
    return scrape_jobs("Automattic", job_ids, queries, greenhouse_jobs, board="automatticcareers")
