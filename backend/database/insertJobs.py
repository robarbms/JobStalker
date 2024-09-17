from .connection import connect_to_db
from .getJobs import get_jobs

# Checks if a job already exists in the database
def in_db(jobs, job, company_id=None) -> bool:
    for db_job in jobs:
        if db_job['job_id'] == job['job_id'] and db_job['company'] == company_id[job['company']]:
            return True
        
    return False

# Helper function that associates a company name to it's id in the database
def get_company_ids(cur=None, conn=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()

    company_query = "SELECT id, name FROM companies"
    cur.execute(company_query)
    companies = cur.fetchall()
    company_id = {}

    for company in companies:
        company_id[company[1]] = company[0]

    return company_id
    
# Inserts a list of jobs
def insert_jobs (jobs, cur=None, conn=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()
    
    company_id = get_company_ids(cur, conn)


    db_jobs = get_jobs(cur, conn)

    for job in jobs:
        if in_db(db_jobs, job, company_id) == False:
            insert_job(job, cur, conn, company_id)
    
    cur.close()
    conn.commit()

# Inserts a job into the database    
def insert_job(job, cur=None, conn=None, company_id=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()
    
    if company_id == None:
        company_id = get_company_ids(cur, conn)

    insert_query = "INSERT INTO jobs (job_id, title, description, location, company_id, salary_min, salary_max, date_posted, link, notes, summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(insert_query,(job['job_id'], job['title'], job['description'], job['location'], company_id[job['company']], job['salary_min'], job['salary_max'], job['date_posted'], job['link'], job['notes'], job['summary']))
