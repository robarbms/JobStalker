from .board_scraper import scrape_jobs, tiktok_jobs


def getTikTokJobs(job_ids, queries=None):
    return scrape_jobs("TikTok", job_ids, queries, tiktok_jobs)
