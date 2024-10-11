# JobStalker
Project for monitoring and searching through job listings.

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

## Frontend
A web application that displays the job listings from the backend service. The user can search for specific keywords in the role title or description text and filter by company.

**Technologies:**
- Node.js
- Express.js
- Webpack
- React
- Typescript
- Recharts

### Job Search
Supports a combination of union, intersection, and exclusion operators to allow users to specify their search criteria.

### Data Visualization
Provides visualizations such as charts and graphs using Recharts, that show the distribution of job listings across different companies and over time.
