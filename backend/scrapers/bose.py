from .board_scraper import scrape_jobs, workday_jobs


def getBoseJobs(job_ids, queries=None):
    return scrape_jobs(
        "Bose", job_ids, queries, workday_jobs,
        host="https://boseallaboutme.wd503.myworkdayjobs.com",
        tenant="boseallaboutme", site="Bose_Careers",
    )
