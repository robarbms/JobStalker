from .board_scraper import ashby_jobs, scrape_jobs


def getHelpScoutJobs(job_ids, queries=None):
    return scrape_jobs("Help Scout", job_ids, queries, ashby_jobs, board="helpscout")
