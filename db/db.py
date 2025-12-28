import mysql.connector
from mysql.connector import Error
from datetime import date
from config import DB_config
from db.utils import hash_password

#  Connection Helper 

def get_connection():
    """
    Create and return a new MySQL database connection
    """
    return mysql.connector.connect(**DB_config)


# . Authentication .

def verify_resident_login(resident_id: str, password: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT Resident_ID, Resident_Name, Block_name, Flat_No, password_hash "
        "FROM resident WHERE Resident_ID=%s",
        (resident_id,)
    )

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and user["password_hash"] == hash_password(password):
        return {
            "Resident_ID": user["Resident_ID"],
            "Resident_Name": user["Resident_Name"],
            "Block_name": user["Block_name"],
            "Flat_No": user["Flat_No"]
        }

    return None


def verify_admin_login(admin_id: str, password: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT Admin_ID, Admin_Name, password_hash "
        "FROM society_admin WHERE Admin_ID=%s",
        (admin_id,)
    )

    admin = cur.fetchone()

    # attempt to fetch Block_name if the column exists
    block_name = None
    try:
        cur.execute("SHOW COLUMNS FROM society_admin LIKE 'Block_name'")
        if cur.fetchone():
            cur.execute(
                "SELECT Block_name FROM society_admin WHERE Admin_ID=%s",
                (admin_id,)
            )
            row = cur.fetchone()
            if row:
                block_name = row.get('Block_name') if isinstance(row, dict) else row[0]
    except Exception:
        block_name = None

    cur.close()
    conn.close()

    if admin and admin["password_hash"] == hash_password(password):
        result = {
            "Admin_ID": admin["Admin_ID"],
            "Admin_Name": admin["Admin_Name"]
        }
        if block_name:
            result["Block_name"] = block_name
        return result

    return None


# . Resident Registration .

def register_resident(
    resident_id: str,
    name: str,
    email: str,
    contact: str,
    block: str,
    flat_no: int,
    password: str
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ check if resident already exists
        cur.execute(
            "SELECT 1 FROM resident WHERE Resident_ID=%s",
            (resident_id,)
        )
        if cur.fetchone():
            return False, "Resident ID already registered"

        # 2️⃣ insert new resident
        cur.execute(
            """
            INSERT INTO resident
            (Resident_ID, Resident_Name, Email, Contact_No,
             Block_name, Flat_No, password_hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                resident_id,
                name,
                email,
                contact,
                block,
                flat_no,
                hash_password(password)
            )
        )

        conn.commit()
        return True, "Resident registered successfully"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()



# . Personnel .

def list_personnel():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT Personnel_ID, Personnel_Name,
               Specialization, Contact_No, Is_Available
        FROM repair_personnel
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


def add_personnel(
    personnel_id: str,
    name: str,
    email: str,
    contact: str,
    specialization: str
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO repair_personnel
            (Personnel_ID, Personnel_Name, Email,
             Contact_No, Specialization, Is_Available)
            VALUES (%s,%s,%s,%s,%s,1)
            """,
            (personnel_id, name, email, contact, specialization)
        )
        conn.commit()
        return True, "Personnel added successfully"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()


def set_personnel_availability(personnel_id: str, available: bool):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE repair_personnel
            SET Is_Available=%s
            WHERE Personnel_ID=%s
            """,
            (1 if available else 0, personnel_id)
        )
        conn.commit()
        return True, "Availability updated"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()


# . Repair Requests .

def create_repair_request(
    request_id: str,
    resident_id: str,
    issue_description: str,
    req_date: date | None = None
):
    if req_date is None:
        req_date = date.today()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO repair_request
            (Request_ID, Resident_ID, Req_Status,
             Issue_Description, Req_Date)
            VALUES (%s,%s,'Pending',%s,%s)
            """,
            (request_id, resident_id, issue_description, req_date)
        )
        conn.commit()
        return True, "Repair request created"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()


def get_requests_for_resident(resident_id: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT r.Request_ID,
               r.Req_Status,
               r.Issue_Description,
               r.Req_Date,
               r.Completion_Date,
               r.Personnel_ID,
               p.Personnel_Name
        FROM repair_request r
        LEFT JOIN repair_personnel p
        ON r.Personnel_ID = p.Personnel_ID
        WHERE r.Resident_ID=%s
        ORDER BY r.Req_Date DESC
        """,
        (resident_id,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


def get_all_requests():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT r.Request_ID,
               r.Resident_ID,
               res.Resident_Name,
               res.Flat_No,
               r.Personnel_ID,
               p.Personnel_Name,
               r.Req_Status,
               r.Issue_Description,
               r.Req_Date,
               r.Completion_Date
        FROM repair_request r
        LEFT JOIN resident res
            ON r.Resident_ID = res.Resident_ID
        LEFT JOIN repair_personnel p
            ON r.Personnel_ID = p.Personnel_ID
        ORDER BY r.Req_Date DESC
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


def get_requests_for_block(block_name: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT r.Request_ID,
               r.Resident_ID,
               res.Resident_Name,
               res.Flat_No,
               r.Personnel_ID,
               p.Personnel_Name,
               r.Req_Status,
               r.Issue_Description,
               r.Req_Date,
               r.Completion_Date
        FROM repair_request r
        LEFT JOIN resident res
            ON r.Resident_ID = res.Resident_ID
        LEFT JOIN repair_personnel p
            ON r.Personnel_ID = p.Personnel_ID
        WHERE res.Block_name = %s
        ORDER BY r.Req_Date DESC
        """,
        (block_name,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


def search_requests(block_name: str | None = None, q: str | None = None, status: str | None = None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    base = (
        "SELECT r.Request_ID,"
        " r.Resident_ID,"
        " res.Resident_Name,"
        " res.Flat_No,"
        " r.Personnel_ID,"
        " p.Personnel_Name,"
        " r.Req_Status,"
        " r.Issue_Description,"
        " r.Req_Date,"
        " r.Completion_Date"
        " FROM repair_request r"
        " LEFT JOIN resident res ON r.Resident_ID = res.Resident_ID"
        " LEFT JOIN repair_personnel p ON r.Personnel_ID = p.Personnel_ID"
    )

    where_clauses = []
    params = []

    if block_name:
        where_clauses.append("res.Block_name = %s")
        params.append(block_name)

    if status:
        where_clauses.append("LOWER(r.Req_Status) = %s")
        params.append(status.lower())

    if q:
        # search in Request_ID and Issue_Description
        where_clauses.append("(CAST(r.Request_ID AS CHAR) LIKE %s OR LOWER(r.Issue_Description) LIKE %s)")
        like_q = f"%{q.lower()}%"
        params.extend([like_q, like_q])

    query = base
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY r.Req_Date DESC"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def assign_personnel_to_request(request_id: str, personnel_id: str):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE repair_request
            SET Personnel_ID=%s,
                Req_Status='Assigned'
            WHERE Request_ID=%s
            """,
            (personnel_id, request_id)
        )

        cur.execute(
            """
            UPDATE repair_personnel
            SET Is_Available=0
            WHERE Personnel_ID=%s
            """,
            (personnel_id,)
        )

        conn.commit()
        return True, "Personnel assigned"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()

def request_id_exists(request_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM repair_request WHERE Request_ID = %s",
        (request_id,)
    )

    exists = cur.fetchone() is not None

    cur.close()
    conn.close()
    return exists

def update_request_status(
    request_id: str,
    status: str,
    completion_date: date | None = None
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if completion_date:
            cur.execute(
                """
                UPDATE repair_request
                SET Req_Status=%s,
                    Completion_Date=%s
                WHERE Request_ID=%s
                """,
                (status, completion_date, request_id)
            )
        else:
            cur.execute(
                """
                UPDATE repair_request
                SET Req_Status=%s
                WHERE Request_ID=%s
                """,
                (status, request_id)
            )

        if status.lower() in ("completed", "closed", "resolved"):
            cur.execute(
                "SELECT Personnel_ID FROM repair_request WHERE Request_ID=%s",
                (request_id,)
            )
            row = cur.fetchone()
            if row and row[0]:
                cur.execute(
                    """
                    UPDATE repair_personnel
                    SET Is_Available=1
                    WHERE Personnel_ID=%s
                    """,
                    (row[0],)
                )

        conn.commit()
        return True, "Status updated"

    except Error as e:
        return False, str(e)

    finally:
        cur.close()
        conn.close()
        