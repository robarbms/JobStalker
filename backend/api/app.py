from flask import Flask, jsonify
from flask_cors import CORS
from connection import connect_to_db

app = Flask(__name__)
CORS(app)

def getCompanyName(companies, companyId):
    for company in companies:
        if company[0] == companyId:
            return company[1]
        
    return ""

@app.route("/api", methods=['GET'])
def api():
    try:
        cur, conn = connect_to_db()
        # Get all the companies from the database
        company_query = "SELECT id, name FROM companies"
        cur.execute(company_query)
        companies = cur.fetchall()

        # Get all the jobs from the database table
        jobs_query = "SELECT id, job_id, title, company_id, created_at, date_posted, link, tags, salary_min, salary_max, summary FROM jobs"
        cur.execute(jobs_query)
        jobs = cur.fetchall()
        conn.close()

        job_results = [
            {'id': row[0], 'job_id': row[1], 'title': row[2], 'company': getCompanyName(companies=companies, companyId=row[3]), 'created_at': row[4], 'date_posted': row[5], 'link': row[6], 'tags': row[7], 'salary_min': row[8], 'salary_max': row[9], 'summary': row[10]}
            for row in jobs
        ]
    
        return jsonify(job_results), 200

    except Exception as e:
        print("Error: {0}".format(e))

    finally:
        conn.close()

if __name__== '__main__':
    app.run(debug=True)
