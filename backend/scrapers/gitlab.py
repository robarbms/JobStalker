from .board_scraper import greenhouse_jobs, scrape_jobs


def getGitLabJobs(job_ids, queries=None):
    return scrape_jobs("GitLab", job_ids, queries, greenhouse_jobs, board="gitlab")
