from connection import connect_to_db

""" create tables in the database"""
def createTables(cur, conn):
    commands = (
        """
       CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL UNIQUE,
            address TEXT,
            site_url TEXT,
            phone_number VARCHAR(20),
            email VARCHAR(255),
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            stock VARCHAR(10),
            founded_date DATE,
            parent_company INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255),
            company_id INTEGER REFERENCES companies(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            salary_min DECIMAL(10, 2),
            salary_max DECIMAL(10, 2),
            date_posted DATE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            link TEXT,
            notes TEXT,
            summary TEXT,
            team TEXT,
            tags TEXT,
            education TEXT,
            experience TEXT,
            leadership BOOLEAN NOT NULL DEFAULT FALSE,
            level TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            firstName VARCHAR(255),
            lastName VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            phone VARCHAR(20)
        )
        """
    )

    try:
        print("Creating tables")
        # execute the commands using the execute() method of the cursor object
        for command in commands:
            cur.execute(command)

        conn.commit() # commit the changes to the database
        
    except (Exception) as error:
        print("Error: %s" % error)

companies = [
    {
        "name": "Apple",
        "address": "Cupertino, CA",
        "site_url": "https://www.apple.com",
        "stock": "AAPL",
    },
    {
        "name": "Netflix",
        "address": "Los Gatos, CA",
        "site_url": "https://www.netflix.com",
        "stock": "NFLX",
    },
    {
        "name": "Microsoft",
        "address": "Redmond, WA",
        "site_url": "https://www.microsoft.com",
        "stock": "MSFT",
    },
    {
        "name": "Adobe",
        "address": "San Jose, CA",
        "site_url": "https://www.adobe.com",
        "stock": "ADBE",
    },
    {
        "name": "Nvidia",
        "address": "Santa Clara, CA",
        "site_url": "https://www.nvidia.com",
        "stock": "NVDA",
    },
    {
        "name": "OpenAI",
        "address": "San Francisco, CA",
        "site_url": "https://www.openai.com",
        "stock": "",
    },
    {
        "name": "Amazon",
        "address": "Seattle, WA",
        "site_url": "https://www.amazon.com",
        "stock": "AMZN",
    },
    {
        "name": "Anthropic",
        "address": "San Francisco, CA",
        "site_url": "https://www.anthropic.com",
        "stock": "",
    },
    {
        "name": "Meta",
        "address": "Menlo Park, CA",
        "site_url": "https:///www.meta.com",
        "stock": "META",
    },
    {
        "name": "Google",
        "address": "Mountain View, CA",
        "site_url": "https://www.google.com",
        "stock": "GOOG",
    },
    {
        "name": "Salesforce",
        "address": "San Francisco, CA",
        "site_url": "https://www.salesforce.com",
        "stock": "CRM",
    },
    {
        "name": "Zillow",
        "address": "Seattle, WA",
        "site_url": "https://www.zillow.com",
        "stock": "Z",
    },
]

# Function to add companies to the DB
# TODO: This should be replace with a method that lets scrapers add companies
def addCompanies(cur, conn, companies):
    print("Adding companies")
    for company in companies:
        addCompany(cur, conn, company)


def addCompany(cur, conn, company_info):
    # Check if the company already exists
    check_query = f"SELECT id, name FROM companies WHERE name='{company_info['name']}'"
    cur.execute(check_query)
    company_found = cur.fetchall()
    # If the company already exists, skip it
    if company_found and len(company_found) > 0:
        return

    insert_query = f"INSERT INTO companies (name, address, site_url, stock) VALUES ('{company_info['name']}', '{company_info['address']}', '{company_info['site_url']}', '{company_info['stock']}')"
    cur.execute(insert_query)
    conn.commit()

# Creates the db tables and adds the companies
def setupDB():
    cur, conn = connect_to_db()
    createTables(cur, conn)
    addCompanies(cur, conn, companies)
    # Checking companies
    company_query = "SELECT * FROM companies"
    cur.execute(company_query)
    found_companies = cur.fetchall()
    print(f"Found company count: {len(found_companies)}")
    
# Method for setting up the database if the file is evoked directly
if __name__ == "__main__":
    setupDB()