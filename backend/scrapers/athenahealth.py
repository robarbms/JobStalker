from .board_scraper import scrape_jobs, workday_jobs


def getAthenahealthJobs(job_ids, queries=None):
    return scrape_jobs(
        "athenahealth", job_ids, queries, workday_jobs,
        host="https://athenahealth.wd1.myworkdayjobs.com",
        tenant="athenahealth", site="External",
    )
