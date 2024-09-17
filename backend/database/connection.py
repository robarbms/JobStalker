import psycopg2
from dotenv import load_dotenv
import os

"""
Function for creating a connection to the database
"""
def connect_to_db():
    # Load environment variables from .env file
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

        return cur, conn
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)

        return None, None
