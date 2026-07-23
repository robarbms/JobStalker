from scrapers import getAllJobs, log
from database import insert_jobs, connect_to_db, get_job_ids, get_jobs
import time
from processing import processJobs
from ai import get_summary
from scrapers.scraper_utils import get_queries
from scrapers.zillow import getJobs

def updateTagsAndSalary(curr, conn):
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
    cur, conn = connect_to_db()
    job_ids = get_job_ids(cur, conn)
    log(f"Fetched job_ids: {len(job_ids)}")
    job_found_count = 0
    total_found = 0
    added_to_db = 0
    queries = get_queries()
    query_index = 0
    for query in queries:
        query_index += 1
        print(f"=======QUERY: '{query}': {query_index}/{len(queries)}========")
        jobs, found = getAllJobs(job_ids, [query])
        job_found_count += len(jobs)
        total_found += found


        updated_jobs = processJobs(jobs)
        for x in range(len(updated_jobs)):
            # push new job ids back into the ids fetched from the database
            eval_job = updated_jobs[x]
            job_ids[eval_job['company']].append(eval_job['job_id'])

            if len(updated_jobs) > x and 'description' in updated_jobs[x]:
                job_description = updated_jobs[x]['description']
                summary = get_summary(job_description)
                updated_jobs[x]['summary'] = summary
        if len(updated_jobs) > 0:
            log(f"Adding {len(updated_jobs)} jobs to database")
            new_job_count = insert_jobs(updated_jobs, cur, conn)
            added_to_db += new_job_count
            log(f"Successfully added {new_job_count} new job(s) to the database")

    # Zillow doesn't have queries so just get them all
    # print(f">>>>>> Zillow scraping")
    # ids = []
    # if 'Zillow' in job_ids:
    #     ids = job_ids['Zillow']
    # jobs_found = getJobs(ids)
    # print(f">>>>>> Found {len(jobs_found)} new jobs for Zillow")
    # updated_zillow_jobs = processJobs(jobs_found)
    # for x in range(len(updated_zillow_jobs)):
    #     if len(updated_zillow_jobs) > x and 'description' in updated_zillow_jobs[x]:
    #         job_description = updated_zillow_jobs[x]['description']
    #         summary = get_summary(job_description)
    #         updated_zillow_jobs[x]['summary'] = summary

    # log(f"Adding {len(updated_jobs)} jobs to database")
    # new_job_count = insert_jobs(updated_jobs, cur, conn)
    # log(f"Successfully added {new_job_count} new job(s) to the database")
    # log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", None)

    log(f"Inserted {added_to_db} jobs for {job_found_count}/{total_found} jobs found.")
    log(f"Finished scraping jobs")

    time.sleep(60 * 60 * 2.1) # sleep for 2 hours and a bit to avoid getting banned from websites
    main()

if __name__ == "__main__": 
    main()
