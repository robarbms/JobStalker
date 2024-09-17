import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
host = os.getenv("DB_HOST")  # Get the host from environment variables
port = os.getenv("DB_PORT")  # Get the port from environment variables
dbname = os.getenv("DB_NAME")  # Get the database name from environment variables
user = os.getenv("DB_USER")  # Get the username from environment variables
password = os.getenv("DB_PASSWORD")  # Get the password from environment variables



@app.route("/")
def api():
    return "Hello, World!"