from .connection import connect_to_db

def get_job_ids(cur=None, conn=None):
    company_ids = {}
    hasConnection = False
    if conn is None or cur is None:
        cur, conn = connect_to_db()
    else:
        hasConnection = True
    company_query = "SELECT id, name FROM companies"
    cur.execute(company_query)
    companies = cur.fetchall()


    for id, name in companies:
        # Get all the jobs from the database table
        jobs_query = "SELECT job_id FROM jobs WHERE company_id={id}".format(id=id)
        cur.execute(jobs_query)
        jobs = cur.fetchall()
        company_ids[name] = [job[0] for job in jobs]

    if hasConnection == False:
        conn.close()
    return company_ids
