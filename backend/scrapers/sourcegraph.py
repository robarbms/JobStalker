from .board_scraper import greenhouse_jobs, scrape_jobs


def getSourcegraphJobs(job_ids, queries=None):
    return scrape_jobs("Sourcegraph", job_ids, queries, greenhouse_jobs, board="sourcegraph91")
