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

Meta data is extracted about each job and stored in a PostgreSQL database. It captures things such as role title, company name, job id, location and description text.

### Database API
Serves jobs to the frontend using Flask.

