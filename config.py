import os
from dotenv import load_dotenv

load_dotenv()  # loads .env

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

# Database Config

import mysql.connector
# Database config
DB_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}
try:
    conn = mysql.connector.connect(**DB_config)
    print("Connected OK")
    conn.close()
except Exception as e:
    print("Connection error:", e)
