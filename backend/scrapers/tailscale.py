from .board_scraper import greenhouse_jobs, scrape_jobs


def getTailscaleJobs(job_ids, queries=None):
    return scrape_jobs("Tailscale", job_ids, queries, greenhouse_jobs, board="tailscale")
