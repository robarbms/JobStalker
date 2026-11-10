## Backend Services
Backend services get jobs, process the data, store it in a database and serve it to the frontend.

### Job Scraper
A service written in Python that searches and retrieves job listings from job boards for several technology companies. It uses a list of queries for common job roles across the companies. The scraper uses Playwright and Beautiful Soup to load and interact with web pages to extract the data that it needs. Each scraper is tailored for the specific job board that it runs on.

**Seattle-targeted companies:**
- Adobe
- Amazon
- Apple
- Google
- Expedia
- Zillow

**Remote-targeted companies:**
- Meta
- Salesforce
- Microsoft
- Netflix
- Nvidia
- Airbnb
- Atlassian
- Blizzard
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
- Dropbox
- Grafana Labs
- Automattic
- Buffer
- Tailscale
- Help Scout
- 37signals
- Supabase
- Ashby
- Close
- Customer.io
- Linear
- Webflow
- Sourcegraph
- Fueled
- Canonical
- PostHog

**Boston-targeted companies:**
- MathWorks
- Akamai Technologies
- InterSystems
- CarGurus
- athenahealth
- Bose
- HubSpot
- Toast
- Klaviyo
- Datadog
- Rapid7

Meta data is extracted about each job and stored in a PostgreSQL database. It captures things such as role title, company name, job id, location and description text.

All employers previously listed under "Scrapers to add" are implemented. Buffer
is registered once. Meta and Salesforce remain disabled in the collection runner.

### Database API
Serves jobs to the frontend using Flask.


## Employer job feeds

The employers previously listed under "Scrapers to add" are registered in
`scrapers\getAllJobs.py`. SerpAPI and DuckDuckGo collect those companies' own
vacancies, not search-engine results; no API key is needed.

The new scrapers use public job feeds or career-page HTML with `requests` and
Beautiful Soup. Shared adapters in `scrapers\board_scraper.py` handle Greenhouse,
Ashby, Lever, Jibe/iCIMS, Oracle Recruiting, Workday, and RSS/Atom feeds.
MathWorks uses its official RSS feed, 37signals its Atom feed, and Rapid7 its
paginated careers table and JobPosting metadata. Square is filtered to the
Square brand on Block's board, Redfin to Redfin Corporation on Rocket's board,
Hulu to Disney's Hulu search results, and Pandora to role-specific mentions on
SiriusXM's board rather than shared company boilerplate.

Each entry point takes `(job_ids, queries=None)` and returns `(new_jobs, found)`.
Queries match job titles case-insensitively within the company's search target.
`None` loads the configured queries, `[]` does no work, and `[""]` matches all
titles. IDs are normalized to strings, and `found` counts unique matching
postings in the shared feed adapters, including known jobs. Legacy browser
scrapers retain their upstream result counts, before local location filtering.
Unknown posting dates and salaries are left `None` rather than invented.
Full descriptions are included for new jobs.

HTTP errors, unexpected markup, and stalled pagination raise `ScraperError`.
The collection runner logs these failures and continues with the other boards.
Public sites can still rate-limit or block automated access, especially LinkedIn;
the scrapers do not bypass login pages or security challenges.
Rapid7 intermittently returns an AWS security challenge. Its listing markup was
verified publicly and its parser is covered offline, but live detail collection
could not be verified reliably.
37signals currently advertises no openings; an empty valid feed is not an error.

### Location targets

`scrapers\company_locations.py` defines company search targets separately from
headquarters and the actual posting location. The collection runner filters
legacy results too; Zillow's separate collection path uses the same policy.
The targets above are based on existing search filters, not headquarters.
Nvidia's existing Workday filter is US Remote, so it remains Remote.

Boston includes Massachusetts metro locations such as Cambridge, Natick,
Framingham, Watertown, and Waltham. Seattle includes Washington metro locations
such as Bellevue, Redmond, and Kirkland, but not unrelated Washington cities.
Suburbs require state information to avoid matching Cambridge, UK or
Burlington, Vermont. Remote requires an explicit remote/home-based location,
remote title, or structured remote work-mode flag. Hybrid and on-site roles are
excluded from Remote targets; descriptions mentioning remote work are not enough.
Unknown locations are excluded rather than guessed. Posting locations are
preserved; target labels do not overwrite them or the database headquarters field.

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
