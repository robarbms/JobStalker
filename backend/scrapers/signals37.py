from .board_scraper import scrape_jobs, signals_jobs


def get37signalsJobs(job_ids, queries=None):
    return scrape_jobs("37signals", job_ids, queries, signals_jobs)
