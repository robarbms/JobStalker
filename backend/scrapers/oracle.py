from .board_scraper import oracle_jobs, scrape_jobs


def getOracleJobs(job_ids, queries=None):
    return scrape_jobs(
        "Oracle", job_ids, queries, oracle_jobs,
        host="https://eeho.fa.us2.oraclecloud.com", site="CX_45001",
        careers_url="https://careers.oracle.com/en/sites/jobsearch",
    )
