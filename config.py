import os
import mysql.connector
from dotenv import load_dotenv

# Load .env only locally
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False  

DB_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

def get_db_connection():
    return mysql.connector.connect(**DB_config)
