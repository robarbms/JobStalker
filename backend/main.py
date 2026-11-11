import os
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database import get_jobs
from backend.scrape_worker import run_forever

def updateTagsAndSalary(curr, conn):
    from backend.processing import processJobs
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

        curr.execute(query)

    conn.commit()

def updateSummary(curr, conn):
    import time
    from backend.ai import get_summary
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

    conn.commit()

def createCompanyMap(ids):
    id_map = {}
    for key in ids:
        company_ids = ids[key]
        id_map[key] = {}
        for job_id in company_ids:
            id_map[key][job_id] = True

    return id_map

def main():
    os.chdir(Path(__file__).resolve().parent)
    run_forever()

if __name__ == "__main__": 
    main()
