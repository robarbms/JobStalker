from scrapers import getAllJobs
from database import insert_jobs


def main():
    jobs = getAllJobs()
    print(f"Found {len(jobs)} jobs")
    print("Adding jobs to database")
    insert_jobs(jobs)

if __name__ == "__main__":
    main()
