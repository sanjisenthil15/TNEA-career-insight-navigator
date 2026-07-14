import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

db_path = BASE_DIR / "database" / "tnea.db"

dataset_path = BASE_DIR / "datasets"

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

print("="*60)
print("Creating Tables...")
print("="*60)
# -------------------------------------------------------
# Create Colleges Table
# -------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS colleges(
    college_code INTEGER PRIMARY KEY,
    college_name TEXT,
    district TEXT,
    college_type TEXT
)
""")

# -------------------------------------------------------
# Create Branches Table
# -------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS branches(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_code INTEGER,
    branch_code TEXT,
    branch_name TEXT
)
""")

# -------------------------------------------------------
# Create Cutoffs Table
# -------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS cutoffs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    college_code INTEGER,
    branch_code TEXT,
    oc REAL,
    bc REAL,
    bcm REAL,
    mbc REAL,
    sc REAL,
    sca REAL,
    st REAL,
    oc_partial REAL,
    bc_partial REAL,
    bcm_partial REAL,
    mbc_partial REAL,
    sc_partial REAL,
    sca_partial REAL,
    st_partial REAL
)
""")

conn.commit()

print("Tables Created Successfully.")
print("="*60)
# -------------------------------------------------------
# Import Colleges
# -------------------------------------------------------

print("Importing colleges...")

colleges = pd.read_csv(dataset_path / "colleges_clean.csv")

colleges = colleges.rename(columns={
    "College Code": "college_code",
    "College Name": "college_name",
    "District": "district"
})

# colleges.csv has no college_type column
colleges["college_type"] = ""

colleges = colleges[
    [
        "college_code",
        "college_name",
        "district",
        "college_type"
    ]
]
colleges.to_sql(
    "colleges",
    conn,
    if_exists="replace",
    index=False
)

print(f"Imported {len(colleges)} colleges")

# -------------------------------------------------------
# Import Branches
# -------------------------------------------------------
print("Creating branches table from cutoff files...")

branch_frames = []

for year in [2023, 2024, 2025]:
    df = pd.read_csv(dataset_path / f"cutoff_{year}.csv")
    branch_frames.append(
        df[["college_code", "branch_code", "branch_name"]]
    )

branches = pd.concat(branch_frames)

# Make branch names consistent
branches["branch_name"] = (
    branches["branch_name"]
    .str.strip()
    .str.upper()
)

# Remove duplicates using only College Code + Branch Code
branches = branches.drop_duplicates(
    subset=["college_code", "branch_code"]
)
branches.to_sql(
    "branches",
    conn,
    if_exists="replace",
    index=False
)

print(f"Imported {len(branches)} unique branches")
# -------------------------------------------------------
# Import Cutoff Data
# -------------------------------------------------------

all_cutoffs = []

for year in [2023, 2024, 2025]:

    print(f"Importing cutoff {year}...")

    df = pd.read_csv(dataset_path / f"cutoff_{year}.csv")

    df["year"] = year

    df = df[[
        "year",
        "college_code",
        "branch_code",
        "oc",
        "bc",
        "bcm",
        "mbc",
        "sc",
        "sca",
        "st",
        "oc_partial",
        "bc_partial",
        "bcm_partial",
        "mbc_partial",
        "sc_partial",
        "sca_partial",
        "st_partial"
    ]]

    all_cutoffs.append(df)

cutoffs = pd.concat(all_cutoffs, ignore_index=True)

cutoffs.to_sql(
    "cutoffs",
    conn,
    if_exists="replace",
    index=False
)

print(f"Imported {len(cutoffs)} cutoff records")
# -------------------------------------------------------
# Finish
# -------------------------------------------------------

conn.commit()
conn.close()

print("=" * 60)
print("DATABASE CREATED SUCCESSFULLY")
print("=" * 60)
print("Database :", db_path)
print("Tables : colleges, branches, cutoffs")