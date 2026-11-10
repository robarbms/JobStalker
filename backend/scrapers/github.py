from .board_scraper import jibe_jobs, scrape_jobs


def getGitHubJobs(job_ids, queries=None):
    return scrape_jobs("GitHub", job_ids, queries, jibe_jobs, base_url="https://www.github.careers")
