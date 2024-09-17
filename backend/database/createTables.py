import psycopg2
from dotenv import load_dotenv
import os
from .connection import connect_to_db

"""
Creates the tables in the database that are needed for storing job information
"""
def createTables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
       CREATE TABLE companies (
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
        CREATE TABLE jobs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255),
            company_id INTEGER REFERENCES companies(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            salary DECIMAL(10, 2),
            date_posted DATE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            link TEXT,
            notes TEXT,
            summary TEXT
        )
        """
    )

    cur, conn = connect_to_db()

    # execute the commands using the execute() method of the cursor object
    for command in commands:
        cur.execute(command)

    cur.close() # close the cursor object
    conn.commit() # commit the changes to the database

createTables()