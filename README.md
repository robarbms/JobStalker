# Job Stalker
Project for monitoring and searching through job listings, parsing job listings, agregating job information such as technology requirements.

## Features

### Job listing scrapers
The app will scrape job sites every 2 hours.

Current companies being scrapped are:

- Adobe
- Amazon
- Apple
- Google
- Meta
- Microsoft
- Netflix
- Nvidia
- Salesforce
- Zillow

The scraper will parse information about each job including:

- Title
- Date posted
- Location
- Pay range (if available)
- Technical requirements for the position as tags
- Job description (summarized with Machine Learning)


## Prereq
You will need a few things installed before you start.

- Python: https://www.python.org/downloads/
- Node: https://nodejs.org/en/download
- PostgreSQL: https://www.postgresql.org/download/

## Setup
These are the steps to get the project started. You only need to run this once, the first time you start the project.

1. **Set up the database.**
    Open pgAdmin.
    Create a new database and name it JobStalker.
    You can use the default user `postgres`.
    Create a password.
    Use the default port `5432`

    See documentation for how to setup PostgreSQL: https://www.postgresql.org/docs/

    Create a .env file in the root directory and include the following info:

    ```
    DB_HOST=localhost
    DB_NAME=JobStalker
    DB_USER=postgres
    DB_PASSWORD=[your password here]
    DB_PORT=5432
    ```

2. **Create a python virtual environment.**
    From a terminal window, change directory into the backend directory with the command:
    ```
    cd backend
    ```

    Create a the virtual invironment with the command:
    ```
    python -m venv venv
    ```

3. **Install python packages.**
    If not still in the backend directory, change directory to the backend.
    Start the virtual environment with the command:
    ```
    python .\venv\Scripts\activate
    ```

    Install all of the packages by running 
    ```
    pip install -r requirements.txt
    ```

4. **Install frontend packages.**
    Change into the frontend directory, if in the backend directory run:
    ```
    cd ..\frontend
    ```

    Install all frontend packages by running:
    ```
    npm install
    ```

    Build the frontend with the command:
    ```
    npm build
    ```

## Application start
You will need to do these steps to get the application up and running. If you close any of the terminals or your computer is restarted, you will need to go through this process again.

You can run the startup.bat file in the root directory. Alternatively, you can start each manually.

1. **Start the job scrapers.**
    Open a new terminal and navigate to the root directory.
    Change directory into the backend directory with:
    ```
    cd backend
    ```
    Start the scraper by running:
    ```
    python main.py
    ```

    This will kick of the scraper. Nothing more needs to be done. It will take some time to scrape, aproximately 30mins or more as more scraapers and queries are added. It will kick off scraping every 2 hours.

2. **Start the backend API service.**
    Open a new terminal and navigate to the root directory. This requires a new window as the scraper needs to remain open as it runs.
    Change directory to the api directory with:
    ```
    cd .\backend\api
    ```

    Start the API by running the command
    ```
    python app.py
    ```

3. **Start the frontend.**
    Open a new terminal and navigate to the root directory.
    Change directory to the frontend directory with:
    ```
    cd .\frontend
    ```

    Start the frontend with the command:
    ```
    npm start
    ```

    This will open a new window with the application running. You may see errors if the scrapers have not finished scraping and inserting data into the DB.
