import base64
import csv
import hashlib
import json
import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ==========================================================
# CONFIGURATION
# ==========================================================

YEAR = 2023

BASE_URL = (
    "https://cutoff.tneaonline.org/api/cutoff"
)

# Paste your captcha token here.
# Example:
# TOKEN = "19b7b0fe-8113-45e6-a1c0-5118f662b3c7"

TOKEN = "19b7b0fe-8113-45e6-a1c0-5118f662b3c7"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

KEY_PREFIX = "tnea-portal-aes-2026-static"


# ==========================================================
# AES KEY
# ==========================================================

def generate_key(token: str):

    text = KEY_PREFIX + (token if token else "anonymous")

    sha = hashlib.sha256()

    sha.update(text.encode())

    return sha.digest()


# ==========================================================
# DECRYPT RESPONSE
# ==========================================================

def decrypt_payload(payload, token):

    iv = base64.b64decode(payload["iv"])

    cipher_text = base64.b64decode(payload["data"])

    key = generate_key(token)

    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    decrypted = cipher.decrypt(cipher_text)

    decrypted = unpad(
        decrypted,
        AES.block_size
    )

    return json.loads(
        decrypted.decode("utf-8")
    )


# ==========================================================
# DOWNLOAD ONE PAGE
# ==========================================================

def download_page(page):

    params = {
        "type": "cutoff",
        "year": YEAR,
        "page": page,
        "pageSize": 50
    }

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        params=params
    )

    response.raise_for_status()

    encrypted = response.json()

    return decrypt_payload(
        encrypted,
        TOKEN
    )


print("=" * 60)
print("TNEA Cutoff Downloader")
print("=" * 60)

if TOKEN == "":
    print()
    print("ERROR")
    print("Paste your captcha token first.")
    print()
    exit()

print("Configuration Loaded")
print("Year :", YEAR)
print()
# ==========================================================
# DETERMINE TOTAL NUMBER OF PAGES
# ==========================================================

print("Checking first page...")

first_page = download_page(1)

# ----------------------------------------------------------
# Try to detect where the records are stored
# ----------------------------------------------------------

records = None

if isinstance(first_page, list):
    records = first_page

elif isinstance(first_page, dict):

    for key in [
        "data",
        "rows",
        "items",
        "results",
        "records",
        "cutoff",
        "list"
    ]:

        if key in first_page:

            records = first_page[key]

            break

if records is None:

    print()
    print("Unable to detect record structure.")
    print()
    print("Decrypted response:")
    print(json.dumps(first_page, indent=2))

    exit()

print("Records found on first page :", len(records))

# ----------------------------------------------------------
# Find total records
# ----------------------------------------------------------

total_records = None

if isinstance(first_page, dict):

    for key in [
        "total",
        "count",
        "totalCount",
        "totalRecords",
        "recordsTotal"
    ]:

        if key in first_page:

            total_records = first_page[key]

            break

# ----------------------------------------------------------
# If total is not available, use 3457
# ----------------------------------------------------------

if total_records is None:

    total_records = 3457

PAGE_SIZE = 50

TOTAL_PAGES = (total_records + PAGE_SIZE - 1) // PAGE_SIZE

print("Total Records :", total_records)

print("Total Pages :", TOTAL_PAGES)

print()

# ==========================================================
# DOWNLOAD EVERY PAGE
# ==========================================================

all_records = []

for page in range(1, TOTAL_PAGES + 1):

    print(f"Downloading page {page}/{TOTAL_PAGES}")

    data = download_page(page)

    page_records = None

    if isinstance(data, list):

        page_records = data

    elif isinstance(data, dict):

        for key in [
            "data",
            "rows",
            "items",
            "results",
            "records",
            "cutoff",
            "list"
        ]:

            if key in data:

                page_records = data[key]

                break

    if page_records is None:

        print("Skipping page", page)

        continue

    all_records.extend(page_records)

print()

print("=" * 60)

print("Downloaded")

print(len(all_records), "records")

print("=" * 60)

print()
# ==========================================================
# SAVE TO CSV
# ==========================================================

if len(all_records) == 0:

    print("No records downloaded.")

    exit()

print("Preparing CSV...")

# ----------------------------------------------------------
# Collect every column that exists
# ----------------------------------------------------------

columns = []

seen = set()

for row in all_records:

    if not isinstance(row, dict):
        continue

    for key in row.keys():

        if key not in seen:

            seen.add(key)

            columns.append(key)

print("Columns detected:", len(columns))

OUTPUT_FILE = f"datasets/cutoff_{YEAR}.csv"

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=columns,
        extrasaction="ignore"
    )

    writer.writeheader()

    for row in all_records:

        if isinstance(row, dict):

            writer.writerow(row)

print()
print("=" * 60)
print("SUCCESS")
print("=" * 60)
print(f"CSV saved as: {OUTPUT_FILE}")
print(f"Total records: {len(all_records)}")
print("=" * 60)