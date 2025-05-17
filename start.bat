echo Starting backend API...

start cmd /k "title JobStalker backend api & cd .\backend & .\venv\Scripts\activate & cd .\api & python .\app.py"

echo Starting frontend...

start cmd /k "title JobStalker frontend server & cd .\frontend & npm start"

echo Starting job scraper service...

start cmd /k "title JobStalker job scraper & cd .\backend & .\venv\Scripts\activate & python .\main.py"
