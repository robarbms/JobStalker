from .board_scraper import greenhouse_jobs, scrape_jobs


def getGrafanaJobs(job_ids, queries=None):
    return scrape_jobs("Grafana Labs", job_ids, queries, greenhouse_jobs, board="grafanalabs")
