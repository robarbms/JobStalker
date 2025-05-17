import sqlite3
import os
import sys

"""
Function for creating a connection to the database
"""
def connect_to_db():
    try:
        db_path = os.path.realpath(os.path.dirname(__file__)) + '\\jobs.db'
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("Connected to database")

        return cur, conn
    
    except (Exception) as error:
        print("Error: %s" % error)

        return None, None

