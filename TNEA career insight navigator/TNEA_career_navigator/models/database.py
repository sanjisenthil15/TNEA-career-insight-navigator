import sqlite3
from pathlib import Path

# ==========================================================
# DATABASE LOCATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "tnea.db"

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


print("=" * 60)
print("Database Module Loaded")
print("Database :", DB_PATH)
print("=" * 60)
# ==========================================================
# GET ALL COLLEGES
# ==========================================================

def get_all_colleges():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            college_code,
            college_name,
            district,
            college_type
        FROM colleges
        ORDER BY college_name

    """)

    colleges = cursor.fetchall()

    conn.close()

    return colleges
# ==========================================================
# GET ALL DISTRICTS
# ==========================================================

def get_all_districts():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT DISTINCT district
        FROM colleges
        WHERE district IS NOT NULL
          AND district != ''
        ORDER BY district

    """)

    districts = cursor.fetchall()

    conn.close()

    return districts
# ==========================================================
# GET ALL BRANCHES
# ==========================================================

def get_all_branches():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT DISTINCT
            branch_code,
            branch_name
        FROM branches
        ORDER BY branch_name

    """)

    branches = cursor.fetchall()

    conn.close()

    return branches
# ==========================================================
# RECOMMEND COLLEGES
# ==========================================================

def recommend_colleges(
    cutoff,
    community,
    branch_code,
    district=None,
    year=2025
):

    conn = get_connection()

    cursor = conn.cursor()

    # ------------------------------------------------------
    # Choose the cutoff column based on community
    # ------------------------------------------------------

    community_columns = {
        "OC": "oc",
        "BC": "bc",
        "BCM": "bcm",
        "MBC": "mbc",
        "SC": "sc",
        "SCA": "sca",
        "ST": "st"
    }

    column = community_columns.get(
        community.upper(),
        "oc"
    )

    # ------------------------------------------------------
    # SQL Query
    # ------------------------------------------------------

    query = f"""

    SELECT DISTINCT

        c.college_code,
        c.college_name,
        c.district,

        ct.branch_code,
        b.branch_name,

        ct.{column} AS cutoff

    FROM cutoffs ct

    JOIN colleges c

        ON c.college_code = ct.college_code

    JOIN branches b

        ON
            b.college_code = ct.college_code
            AND
            b.branch_code = ct.branch_code

    WHERE

    ct.year = ?

    AND

    ct.branch_code = ?

    AND

    ct.{column} IS NOT NULL
    """

    parameters = [
    year,
    branch_code
]

    if district:

        query += """

        AND c.district = ?

        """

        parameters.append(district)

    query += """

    ORDER BY

        ct.""" + column + """ DESC

    """

    cursor.execute(
        query,
        parameters
    )

    results = cursor.fetchall()

    conn.close()

    return results
# ==========================================================
# GET SINGLE COLLEGE DETAILS
# ==========================================================

def get_college_details(college_code):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM colleges

        WHERE college_code = ?

    """, (college_code,))

    college = cursor.fetchone()

    conn.close()

    return college
# ==========================================================
# GET ALL BRANCHES OF A COLLEGE
# ==========================================================

def get_college_branches(college_code):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            branch_code,
            branch_name

        FROM branches

        WHERE college_code = ?

        ORDER BY branch_name

    """, (college_code,))

    branches = cursor.fetchall()

    conn.close()

    return branches
# ==========================================================
# GET MULTIPLE COLLEGES FOR COMPARISON
# ==========================================================

def get_compare_colleges(college_codes):

    conn = get_connection()

    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(college_codes))

    query = f"""

        SELECT

            college_code,
            college_name,
            district,
            college_type

        FROM colleges

        WHERE college_code IN ({placeholders})

        ORDER BY college_name

    """

    cursor.execute(query, college_codes)

    colleges = cursor.fetchall()

    conn.close()

    return colleges