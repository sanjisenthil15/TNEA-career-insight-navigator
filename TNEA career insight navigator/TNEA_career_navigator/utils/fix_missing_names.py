import csv
from pathlib import Path

base = Path(__file__).parent.parent

branches_file = base / "datasets" / "branches.csv"
colleges_file = base / "datasets" / "colleges_clean.csv"

# Read all college names
college_names = {}

with open(colleges_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        code = row["College Code"].strip()
        name = row["College Name"].strip()
        college_names[code] = name

updated_rows = []

with open(branches_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        code = row["College Code"].strip()
        name = row["College Name"].strip()

        # Fix missing or incorrect names
        if code in college_names:
            row["College Name"] = college_names[code]

        updated_rows.append(row)

# Save back
with open(branches_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "College Code",
            "College Name",
            "Branch Code",
            "Approved Intake",
            "Year Started",
            "NBA",
            "Accreditation Valid Upto",
        ],
    )

    writer.writeheader()
    writer.writerows(updated_rows)

print("✅ Missing college names fixed successfully.")