from .board_scraper import ashby_jobs, scrape_jobs


def getBufferJobs(job_ids, queries=None):
    return scrape_jobs("Buffer", job_ids, queries, ashby_jobs, board="buffer")
