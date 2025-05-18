import sqlite3
import configparser
import os
import re

def get_config():
    config = configparser.ConfigParser()
    cur_path = os.path.dirname(__file__)
    root_path = re.sub(r"JobStalker.*", "JobStalker", cur_path)
    config_path = root_path + "\\config.ini"
    config.read(config_path)
    scenario = config.get('app', 'scenario')
    return {
        'scenario': scenario
    }

"""
Function for creating a connection to the database
"""
def connect_to_db():
    try:
        config = get_config()
        db_name = f"{config['scenario']}_jobs.db"
        api_path = os.path.realpath(os.path.dirname(__file__))
        backend_path = re.sub('api', '', api_path)
        database_path = backend_path + f"/database/{db_name}"
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        print("Connected to database")

        return cur, conn
    
    except (Exception) as error:
        print("Error: %s" % error)

        return None, None
