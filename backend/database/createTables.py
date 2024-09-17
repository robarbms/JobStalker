import psycopg2
from dotenv import load_dotenv
import os

""" create tables in the PostgreSQL database"""
def createTables():
    commands = (
        """
       CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            team TEXT
        )
        """
    )

    # load environment variables from .env file
    load_dotenv()

    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')

    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )

        print("Connected to database")

       # create a new cursor object using the cursor() method of the connection object
        cur = conn.cursor()

       # execute the commands using the execute() method of the cursor object
        for command in commands:
            cur.execute(command)

        cur.close() # close the cursor object
        conn.commit() # commit the changes to the database
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)

    # close the database connection using the close() method of the connection object
    finally:
        if conn is not None:
            # close the communication with the PostgreSQL
            conn.close()

createTables()