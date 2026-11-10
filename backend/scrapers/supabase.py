from .board_scraper import ashby_jobs, scrape_jobs


def getSupabaseJobs(job_ids, queries=None):
    return scrape_jobs("Supabase", job_ids, queries, ashby_jobs, board="supabase")
