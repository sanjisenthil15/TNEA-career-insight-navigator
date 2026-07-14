import sqlite3

conn = sqlite3.connect("database/tnea.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(branches)")

print("Columns in branches table:\n")

for column in cursor.fetchall():
    print(column)

conn.close()