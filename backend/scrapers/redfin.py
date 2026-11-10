from .board_scraper import scrape_jobs, workday_jobs


def getRedfinJobs(job_ids, queries=None):
    return scrape_jobs(
        "Redfin", job_ids, queries, workday_jobs,
        host="https://quickenloans.wd5.myworkdayjobs.com",
        tenant="quickenloans", site="rocket_careers", employer="Redfin Corporation",
    )
