from .connection import connect_to_db

def get_jobs(cur=None, conn=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()

    select_query = "SELECT * FROM jobs"

    cur.execute(select_query)

    jobs = cur.fetchall()

    return jobs

def get_job_ids(cur=None, conn=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()

    select_query = "SELECT job_id, company_id FROM jobs"

    cur.execute(select_query)

    jobs = cur.fetchall()

    return [{'job_id': job[0], 'company_id': job[1]} for job in jobs]
