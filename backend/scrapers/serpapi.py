from .board_scraper import scrape_jobs, website_jobs


def getSerpAPIJobs(job_ids, queries=None):
    return scrape_jobs(
        "SerpAPI", job_ids, queries, website_jobs,
        url="https://serpapi.com/careers",
        link_pattern=r"https://serpapi\.com/careers/(?P<id>[a-z0-9-]+)",
        description_selector="section.about-career",
        location_selector=".summary li:first-child",
    )
