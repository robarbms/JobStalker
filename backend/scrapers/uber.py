from .board_scraper import oracle_jobs, scrape_jobs


def getUberJobs(job_ids, queries=None):
    return scrape_jobs(
        "Uber", job_ids, queries, oracle_jobs,
        host="https://iaziqy.fa.ocs.oraclecloud.com", site="UberCareers",
        careers_url="https://iaziqy.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/UberCareers",
    )
