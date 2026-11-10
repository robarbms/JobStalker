from .board_scraper import jibe_jobs, scrape_jobs


def getPandoraJobs(job_ids, queries=None):
    return scrape_jobs(
        "Pandora", job_ids, queries, jibe_jobs,
        base_url="https://careers.siriusxm.com", employer="Pandora",
    )
