import sqlite3

"""
Function for creating a connection to the database
"""
def connect_to_db():
    try:
        conn = sqlite3.connect('../database/jobs.db')
        cur = conn.cursor()
        print("Connected to database")

        return cur, conn
    
    except (Exception) as error:
        print("Error: %s" % error)

        return None, None
