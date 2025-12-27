import mysql.connector
from mysql.connector import Error
from config import DB_config


def _get_connection_without_db():
    cfg = DB_config.copy()
    cfg.pop("database")
    return mysql.connector.connect(**cfg)


def initialize_database():
    # 1️⃣ Create database if not exists
    conn = _get_connection_without_db()
    cur = conn.cursor()

    cur.execute(
        "CREATE DATABASE IF NOT EXISTS `{}`".format(DB_config["database"])
    )

    cur.close()
    conn.close()

    # 2️⃣ Create tables
    conn = mysql.connector.connect(**DB_config)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resident (
            Resident_ID VARCHAR(10) PRIMARY KEY,
            Resident_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            Block_name VARCHAR(20),
            Flat_No INT,
            password_hash VARCHAR(128)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS society_admin (
            Admin_ID VARCHAR(10) PRIMARY KEY,
            Admin_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            password_hash VARCHAR(128)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_personnel (
            Personnel_ID VARCHAR(10) PRIMARY KEY,
            Personnel_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            Specialization VARCHAR(50),
            Is_Available TINYINT(1) DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_request (
            Request_ID VARCHAR(15) PRIMARY KEY,
            Resident_ID VARCHAR(10),
            Personnel_ID VARCHAR(10),
            Req_Status VARCHAR(30),
            Issue_Description VARCHAR(500),
            Req_Date DATE,
            Completion_Date DATE,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Resident_ID) REFERENCES resident(Resident_ID),
            FOREIGN KEY (Personnel_ID) REFERENCES repair_personnel(Personnel_ID)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Database and tables initialized successfully")


if __name__ == "__main__":
    initialize_database()
