from scrapers import getAllJobs
from scrapers.utils import log
from database import insert_jobs, connect_to_db, get_job_ids
from scrapers import job
import time

def main():
    job_ids = get_job_ids()
    jobs = getAllJobs(job_ids)
    log("Adding jobs to database")
    new_job_count = insert_jobs(jobs)
    log(f"Successfully added {new_job_count} new job(s) to the database")
    time.sleep(60 * 60 * 2.1) # sleep for 2 hours and a bit to avoid getting banned from websites
    main()

if __name__ == "__main__":
    main()
