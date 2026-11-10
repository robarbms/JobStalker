from .board_scraper import lever_jobs, scrape_jobs


def getSpotifyJobs(job_ids, queries=None):
    return scrape_jobs("Spotify", job_ids, queries, lever_jobs, board="spotify")
