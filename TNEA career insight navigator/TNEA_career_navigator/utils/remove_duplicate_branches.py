import sqlite3

conn = sqlite3.connect("database/tnea.db")
cursor = conn.cursor()

print("Removing duplicate branches...")

cursor.execute("""
CREATE TABLE branches_new AS
SELECT DISTINCT
    college_code,
    branch_code,
    branch_name
FROM branches
""")

cursor.execute("DROP TABLE branches")

cursor.execute("""
ALTER TABLE branches_new
RENAME TO branches
""")

conn.commit()
conn.close()

print("Duplicate branches removed successfully!")