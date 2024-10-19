import json
from .keywords import get_keywords
from .pay import get_pay
import re

# Process job postings by extracting keywords and payment information
# Additional information will be added here to be added to the job
def process(description, title):
    desc_keyword_path = '../frontend/job-stalker/src/utils/'
    keyword_files = ['tech_keywords.json', 'ds_keywords.json']
    keywords = set()

    # Parse keywords in description
    for file in keyword_files:
        file_path = desc_keyword_path + file

        # Import json file with keywords
        with open(file_path, 'r') as f:
            data = json.load(f)

            keywords_found = get_keywords(description, data)
            keywords_title = get_keywords(title, data)
            if keywords_found:
                keywords.update(set(keywords_found))
                keywords.update(set(keywords_title))

    # Get keywords in text
    keywords = list(keywords)

    # Prase pay from description
    salary_min, salary_max = get_pay(description)

    key_str = str(keywords)
    key_str = re.sub(r"'", "\"", key_str)

    return key_str, salary_min, salary_max

# Loops through a list of jobs and gets meta information about each job
def processJobs(jobs):
    for index in range(len(jobs)):
        job = jobs[index]

        tags, salary_min, salary_max = process(job['description'], job['title'])
        job['tags'] = tags
        job['salary_min'] = salary_min
        job['salary_max'] = salary_max
        jobs[index] = job

    return jobs

