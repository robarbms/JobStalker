from .board_scraper import ashby_jobs, scrape_jobs


def getPostHogJobs(job_ids, queries=None):
    return scrape_jobs("PostHog", job_ids, queries, ashby_jobs, board="posthog")
