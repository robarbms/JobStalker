from database import connect_to_db, get_jobs
from processing import process
from ai import get_summary
import time

def update_keywords(job, cur):
    # get keywords
    keywords, salary_min, salary_max = process(job[3], job[2])
    if keywords != job[15]:
        sql = f"UPDATE jobs SET tags='{keywords}' WHERE id='{job[0]}'"
        cur.execute(sql)
        print(sql)
    else:
        print("MATCH!!!!!!")

def update_summary(job, cur):
    description = job[3]
    summary = job[13]
    print(f"updating summary for {job[2]} with description length: {len(description)} and current summary length: {len(summary)}")
    if len(summary) < 10 and description != "":
        ai_summary = get_summary(description)
        sql = f"UPDATE jobs SET summary='{ai_summary}' WHERE id='{job[0]}'"
        cur.execute(sql)
        print(f"Summary length: {len(ai_summary)}")


if __name__ == "__main__": 
    keys = {
        'id': 0,
        'job_id': 1,
        'title': 2,
        'description': 3,
        'location': 4,
        'company_id': 5,
        'created_at': 6,
        'salary_min': 7,
        'salary_max': 8,
        'date_posted': 9,
        'is_active': 10,
        'link': 11,
        'notes': 12,
        'summary': 13,
        'team': 14,
        'tags': 15
    }
    cur, conn = connect_to_db()
    jobs = get_jobs(cur, conn)
    for job in jobs:
        # update_keywords(job, cur)
        if job[13] == None or job[13] == "":
            print(f"Updating job: {job[0]} summary length: {len(job[13])}")
            update_summary(job, cur)
            time.sleep(3)
    conn.commit()
    conn.close()
