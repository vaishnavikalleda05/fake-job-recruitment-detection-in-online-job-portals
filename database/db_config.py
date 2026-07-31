"""
===========================================================
Fake Job Detection in Online Portals
Database Configuration
Author : Kalleda Vaishnavi
===========================================================
"""

import mysql.connector
from mysql.connector import Error

# ==========================================================
# Database Configuration
# ==========================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "fake_job_detection",
    "port": 3306
}


# ==========================================================
# Create Database Connection
# ==========================================================

def get_connection():
    """
    Create and return a MySQL connection.
    """

    try:

        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            print("Connected to MySQL Database")

        return connection

    except Error as e:

        print("Database Connection Error:", e)

        return None


# ==========================================================
# Close Database Connection
# ==========================================================

def close_connection(connection):

    if connection is not None:

        connection.close()

        print("Database Connection Closed")


# ==========================================================
# Execute INSERT / UPDATE / DELETE Queries
# ==========================================================

def execute_query(query, values=None):

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:

        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        connection.commit()

        return True

    except Error as e:

        print(e)

        return False

    finally:

        cursor.close()

        close_connection(connection)


# ==========================================================
# Execute SELECT Queries
# ==========================================================

def fetch_query(query, values=None):

    connection = get_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:

        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        result = cursor.fetchall()

        return result

    except Error as e:

        print(e)

        return []

    finally:

        cursor.close()

        close_connection(connection)


# ==========================================================
# Save Job
# ==========================================================

def save_job(job):

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    query = """
    INSERT INTO jobs
    (
        company_name,
        job_title,
        location,
        salary_range,
        employment_type,
        required_experience,
        required_education,
        industry,
        company_profile,
        job_description,
        requirements,
        benefits,
        contact_email,
        contact_phone,
        has_company_logo,
        has_questions
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        job["company_name"],
        job["job_title"],
        job["location"],
        job["salary_range"],
        job["employment_type"],
        job["required_experience"],
        job["required_education"],
        job["industry"],
        job["company_profile"],
        job["job_description"],
        job["requirements"],
        job["benefits"],
        job["contact_email"],
        job["contact_phone"],
        job["has_company_logo"],
        job["has_questions"]
    )

    try:

        cursor.execute(query, values)

        connection.commit()

        return cursor.lastrowid

    except Error as e:
        print("========== DATABASE ERROR ==========")
        print(e)
        print("===================================")
        return None

    finally:

        cursor.close()

        close_connection(connection)


# ==========================================================
# Save Prediction
# ==========================================================

def save_prediction(job_id,
                    prediction,
                    risk_score,
                    ml_probability,
                    rule_score):

    query = """

    INSERT INTO predictions

    (
        job_id,
        prediction,
        risk_score,
        ml_probability,
        rule_score
    )

    VALUES

    (%s,%s,%s,%s,%s)

    """

    values = (

        job_id,
        prediction,
        risk_score,
        ml_probability,
        rule_score

    )

    return execute_query(query, values)


# ==========================================================
# Get All Jobs
# ==========================================================

def get_all_jobs():

    query = """

    SELECT *

    FROM jobs

    ORDER BY uploaded_at DESC

    """

    return fetch_query(query)


# ==========================================================
# Get All Predictions
# ==========================================================

def get_all_predictions():

    query = """

    SELECT *

    FROM predictions

    ORDER BY predicted_on DESC

    """

    return fetch_query(query)


# ==========================================================
# Get High Risk Jobs
# ==========================================================

def get_high_risk_jobs():

    query = """

    SELECT

    jobs.job_title,
    jobs.company_name,
    predictions.risk_score

    FROM jobs

    JOIN predictions

    ON jobs.job_id=predictions.job_id

    WHERE predictions.risk_score>=80

    ORDER BY predictions.risk_score DESC

    """

    return fetch_query(query)


# ==========================================================
# Dashboard Statistics
# ==========================================================

def dashboard_stats():

    query = """

    SELECT

    COUNT(*) AS TotalJobs,

    SUM(
        CASE
        WHEN prediction='Fake'
        THEN 1
        ELSE 0
        END
    ) AS FakeJobs,

    SUM(
        CASE
        WHEN prediction='Real'
        THEN 1
        ELSE 0
        END
    ) AS RealJobs,

    AVG(risk_score) AS AverageRisk

    FROM predictions

    """

    result = fetch_query(query)

    return result


# ==========================================================
# Search Jobs
# ==========================================================

def search_job(keyword):

    query = """

    SELECT *

    FROM jobs

    WHERE

    company_name LIKE %s

    OR

    job_title LIKE %s

    """

    values = (

        "%" + keyword + "%",
        "%" + keyword + "%"

    )

    return fetch_query(query, values)


# ==========================================================
# Test Connection
# ==========================================================

if __name__ == "__main__":

    connection = get_connection()

    if connection:

        print("Database Connected Successfully")

        close_connection(connection)

    else:

        print("Connection Failed")