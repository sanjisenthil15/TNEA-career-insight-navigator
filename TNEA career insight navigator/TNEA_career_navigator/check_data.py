import sqlite3

conn = sqlite3.connect("database/tnea.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    college_code,
    bc
FROM cutoffs
WHERE branch_code='AT'
AND year=2025
""")

rows = cursor.fetchall()

print(rows)

conn.close()