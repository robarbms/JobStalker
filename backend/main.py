from scrapers import getAllJobs
from scrapers.utils import log
from database import insert_jobs

def main():
    jobs = getAllJobs()
    log("Adding jobs to database")
    new_job_count = insert_jobs(jobs)
    log(f"Successfully added {new_job_count} new job(s) to the database")

if __name__ == "__main__":
    main()
