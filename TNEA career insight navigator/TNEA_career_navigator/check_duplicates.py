import sqlite3

conn = sqlite3.connect("database/tnea.db")
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM branches
WHERE college_code = 1101
AND branch_code = 'AD'
""")

rows = cursor.fetchall()

print("Rows found:", len(rows))

for row in rows:
    print(row)

conn.close()