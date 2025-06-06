from database import connect_to_db, get_jobs
from processing import process

def update_job(job, cur):
    # get keywords
    keywords, salary_min, salary_max = process(job[3], job[2])
    if keywords != job[15]:
        sql = f"UPDATE jobs SET tags='{keywords}' WHERE id='{job[0]}'"
        cur.execute(sql)
        print(sql)
    else:
        print("MATCH!!!!!!")

if __name__ == "__main__": 
    cur, conn = connect_to_db()
    jobs = get_jobs(cur, conn)
    for job in jobs:
        update_job(job, cur)
    conn.commit()
    conn.close()
