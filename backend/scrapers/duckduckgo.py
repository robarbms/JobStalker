from .board_scraper import ashby_jobs, scrape_jobs


def getDuckDuckGoJobs(job_ids, queries=None):
    return scrape_jobs("DuckDuckGo", job_ids, queries, ashby_jobs, board="duck-duck-go")
