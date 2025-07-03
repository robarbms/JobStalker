import json
from .keywords import get_keywords
from .pay import get_pay
import re

# Process job postings by extracting keywords and payment information
# Additional information will be added here to be added to the job
def process(description, title, getPay=False):
    desc_keyword_path = '../frontend/src/utils/'
    keyword_files = ['tech_keywords.json', 'ds_keywords.json', 'design_keywords.json']
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

    salary_min = None
    salary_max = None

    if getPay:
        # Parse pay from description
        salary_min, salary_max = get_pay(description)

    keywords.sort()

    key_str = str(keywords)
    key_str = re.sub(r"'", "\"", key_str)

    return key_str, salary_min, salary_max

# Loops through a list of jobs and gets meta information about each job
def processJobs(jobs):
    for index in range(len(jobs)):
        job = jobs[index]
        missing_salary = 'salary_min' not in job or job['salary_min'] == None or 'salary_max' not in job or job['salary_max'] == None

        if 'title' in job and 'description' in job:
            tags, salary_min, salary_max = process(job['description'], job['title'], missing_salary)
            job['tags'] = f"{tags}"
            if missing_salary:
                if salary_min:
                    job['salary_min'] = salary_min
                if salary_max:
                    job['salary_max'] = salary_max
                jobs[index] = job
        else:
            print(f"Error: Missing property for getting properties. has title: {'title' in job}; has description: {'description' in job}")
            print(f">>> company: {job['company']}")

    return jobs

