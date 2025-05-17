def get_job_ids(cur, conn):
    company_ids = {}

    company_query = "SELECT id, name FROM companies"
    cur.execute(company_query)
    companies = cur.fetchall()

    for id, name in companies:
        # Get all the jobs from the database table
        jobs_query = "SELECT job_id FROM jobs WHERE company_id={id}".format(id=id)
        cur.execute(jobs_query)
        jobs = cur.fetchall()
        company_ids[name] = [job[0] for job in jobs]

    return company_ids
 