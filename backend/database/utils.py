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
