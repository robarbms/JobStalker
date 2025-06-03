from .connection import connect_to_db
from .getJobIds import get_job_ids
import sqlite3

# Checks if a job already exists in the database
def in_db(jobs, job, company_id=None) -> bool:
    for db_job in jobs:
        if db_job['job_id'] == job['job_id'] and db_job['company_id'] == company_id[job['company']]:
            return True
        
    return False

# Helper function that associates a company name to it's id in the database
def get_company_ids(cur, conn):
    company_query = "SELECT id, name FROM companies"
    cur.execute(company_query)
    companies = cur.fetchall()
    company_ids = {}

    for company in companies:
        company_ids[company[1]] = company[0]

    print(company_ids)

    return company_ids
    
# Inserts a list of jobs
def insert_jobs (jobs, cur, conn):
    company_ids = get_company_ids(cur, conn)
    job_ids = get_job_ids(cur, conn)

    jobs_inserted = 0

    for job in jobs:
        try:
            if 'company' in job and 'job_id' in job:
                if job['company'] not in job_ids or job['job_id'] not in job_ids[job['company']]:
                    insert_job(job, cur, conn, company_ids[job['company']])
                    jobs_inserted += 1
            else:
                print("Missing company or job_id")
        except Exception as e:
            print("Error inserting job: ", e)
    
    conn.commit()

    print("Jobs inserted into the database: {0}".format(jobs_inserted))
    return jobs_inserted

# Inserts a job into the database    
def insert_job(job, cur, conn, company_id):
    def escape_quote (str):
        str = str.replace("'", r"\\'")

        return str
    description = job['description']
    description = escape_quote(description)

    try:
        insert_query = "INSERT INTO jobs (job_id, title, description, location, company_id, salary_min, salary_max, date_posted, link, notes, summary, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(insert_query, (job['job_id'], job['title'], job['description'], job['location'], company_id, job['salary_min'], job['salary_max'], job['date_posted'], job['link'], job['notes'], job['summary'], job['tags']))

    except Exception as e:
        print("Error inserting job: ", e)
        print(insert_query)
