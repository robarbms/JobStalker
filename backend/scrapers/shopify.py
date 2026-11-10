from .board_scraper import scrape_jobs, website_jobs


def getShopifyJobs(job_ids, queries=None):
    return scrape_jobs(
        "Shopify", job_ids, queries, website_jobs,
        url="https://www.shopify.com/careers",
        link_pattern=r"https://www\.shopify\.com/careers/[^/]+_(?P<id>[0-9a-f-]{36})",
        description_selector="article section .richtext",
        location_selector="article header p",
    )
