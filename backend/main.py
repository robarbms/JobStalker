from scrapers import getAllJobs
from scrapers.utils import log
from database import insert_jobs, connect_to_db, get_job_ids, get_jobs
import time
from processing import processJobs
from ai import get_summary

def updateTagsAndSalary():
    curr, conn = connect_to_db()
    allJobs = get_jobs(curr, conn)
    updated_jobs = []

    allJobs = [{
        "id": job[0],
        "title": job[2],
        "description": job[3],
    } for job in allJobs]
    updated_jobs = processJobs(allJobs)

    for job in updated_jobs:
        # update row in db to include description and salary info
        id = job['id']
        tags = job['tags']
        salary_min = job['salary_min']
        salary_max = job['salary_max']
        query = f"UPDATE jobs SET tags={tags}"

        if salary_min != None and salary_max != None:
            query += f", salary_min={salary_min}, salary_max={salary_max}"

        query += f" WHERE id={id}"

        print(query)
        curr.execute(query)

    curr.close()
    conn.commit()

def updateSummary():
    curr, conn = connect_to_db()
    allJobs = get_jobs(curr, conn)
    count = 0

    allJobs = [{
        "id": job[0],
        "title": job[2],
        "description": job[3],
        "summary": job[13],
    } for job in allJobs]

    for job in allJobs:
        if job['summary'] == None or len(job['summary']) < 10:
            count += 1
            if count > 1:
                try:
                    summary = get_summary(job['description'])
                    query = f"UPDATE jobs SET summary='{summary}' WHERE id={job['id']}"
                    curr.execute(query)
                    time.sleep(3)
                except Exception as e:
                    print(f"ERROR: on job #{count} ")
                    print(e)
                    curr.close()
                    conn.commit()


    curr.close()
    conn.commit()


def main():

    job_ids = get_job_ids()
    jobs = getAllJobs(job_ids)

    updated_jobs = processJobs(jobs)
    for x in range(len(updated_jobs)):
        job_description = updated_jobs[x]['description']
        summary = get_summary(job_description)
        updated_jobs[x]['summary'] = summary

    log("Adding jobs to database")
    new_job_count = insert_jobs(updated_jobs)
    log(f"Successfully added {new_job_count} new job(s) to the database")
    time.sleep(60 * 60 * 2.1) # sleep for 2 hours and a bit to avoid getting banned from websites
    main()

if __name__ == "__main__": 
    # updateSummary()
    main()
