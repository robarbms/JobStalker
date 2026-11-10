## Backend Services
Backend services get jobs, process the data, store it in a database and serve it to the frontend.

### Job Scraper
A service written in Python that searches and retrieves job listings from job boards for several technology companies. It uses a list of queries for common job roles across the companies. The scraper uses Playwright and Beautiful Soup to load and interact with web pages to extract the data that it needs. Each scraper is tailored for the specific job board that it runs on.

**Companies:**
- Adobe
- Amazon
- Apple
- Google
- Meta
- Microsoft
- Netflix
- Nvidia
- Airbnb
- Atlassian
- Blizzard
- Expedia
- Zillow
- TikTok
- Reddit
- Smartsheet
- GitHub
- LinkedIn
- Uber
- DoorDash
- Oracle
- SerpAPI
- DuckDuckGo
- Mozilla
- Square
- Shopify
- GitLab
- Redfin
- Hulu
- Zapier
- Spotify
- Pandora

Meta data is extracted about each job and stored in a PostgreSQL database. It captures things such as role title, company name, job id, location and description text.

### Database API
Serves jobs to the frontend using Flask.


## Employer job feeds

The employers previously listed under "Scrapers to add" are registered in
`scrapers\getAllJobs.py`. SerpAPI and DuckDuckGo collect those companies' own
vacancies, not search-engine results; no API key is needed.

The new scrapers use public job feeds or career-page HTML with `requests` and
Beautiful Soup. Shared adapters in `scrapers\board_scraper.py` handle Greenhouse,
Ashby, Lever, Jibe/iCIMS, Oracle Recruiting, and Workday. Square is filtered to the
Square brand on Block's board, Redfin to Redfin Corporation on Rocket's board,
Hulu to Disney's Hulu search results, and Pandora to role-specific mentions on
SiriusXM's board rather than shared company boilerplate.

Each entry point takes `(job_ids, queries=None)` and returns `(new_jobs, found)`.
Queries match job titles case-insensitively across all advertised locations.
`None` loads the configured queries, `[]` does no work, and `[""]` matches all
titles. IDs are normalized to strings, and `found` counts unique matching
postings, including known jobs. Unknown posting dates and salaries are left
`None` rather than invented. Full descriptions are included for new jobs.

HTTP errors, unexpected markup, and stalled pagination raise `ScraperError`.
The collection runner logs these failures and continues with the other boards.
Public sites can still rate-limit or block automated access, especially LinkedIn;
the scrapers do not bypass login pages or security challenges.

After updating an existing installation, register the new companies using the
normal setup script (run from the repository root):

```powershell
backend\venv\Scripts\python.exe backend\database\createTables.py
```

## Scraper tests

Run from the repository root after installing the backend dependencies:

```powershell
backend\venv\Scripts\python.exe -m unittest discover -s backend\tests -v
```

Tests use mocked HTTP responses and offline DOM fixtures; they do not contact
job boards, launch browsers, or write to the application database. They cover
all new employer scrapers, the existing Playwright scrapers (including disabled
Meta and Salesforce), collection integration, and company registration.
The unfinished `2k.py` is covered only for its current empty-result behavior;
the obsolete, non-importable OpenAI prototype under `scrapers\archive` is excluded.
