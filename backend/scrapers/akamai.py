from .board_scraper import oracle_jobs, scrape_jobs


def getAkamaiJobs(job_ids, queries=None):
    host = "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com"
    return scrape_jobs(
        "Akamai Technologies", job_ids, queries, oracle_jobs,
        host=host, site="CX_1",
        careers_url=host + "/hcmUI/CandidateExperience/en/sites/CX_1",
        target_location="Boston",
    )
