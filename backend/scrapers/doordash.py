from .board_scraper import greenhouse_jobs, scrape_jobs


def getDoorDashJobs(job_ids, queries=None):
    return scrape_jobs("DoorDash", job_ids, queries, greenhouse_jobs, board="doordashusa")
