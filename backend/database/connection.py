import sqlite3
import os
import sys

# Add the directory of the current script to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_config

"""
Function for creating a connection to the database
"""
def connect_to_db():
    try:
        config = get_config()
        db_name = f'{config['scenario']}_jobs.db'
        db_path = os.path.realpath(os.path.dirname(__file__)) + '\\' + db_name
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("Connected to database")

        return cur, conn
    
    except (Exception) as error:
        print("Error: %s" % error)

        return None, None

