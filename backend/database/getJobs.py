from .connection import connect_to_db

def get_jobs(cur=None, conn=None):
    if cur == None or conn == None:
        cur, conn = connect_to_db()

    select_query = "SELECT * FROM jobs"

    cur.execute(select_query)

    jobs = cur.fetchall()

    return jobs