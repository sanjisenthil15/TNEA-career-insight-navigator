import pdfplumber
import csv
import re
from pathlib import Path

pdf_path = Path(__file__).parent.parent / "Information_About_Colleges.pdf"
output_csv = Path(__file__).parent.parent / "datasets" / "branches.csv"

HEADER_FIELD_PATTERN = re.compile(
    r"\b(?:Bank|Name of the Principal|Dean|A/c No\.?|Address|Distance|Nearest|Taluk|Railway Station|Minority|Pincode|Status|Autonomous|Phone/Fax|EMail-ID|Email|Website|Antiphone|Hostel|Course|Approved|Intake|Starting|NBA|Accredited)\b",
    flags=re.IGNORECASE,
)


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line or "").strip()


def is_header_field(line: str) -> bool:
    return bool(HEADER_FIELD_PATTERN.search(line))


def is_name_candidate(line: str) -> bool:
    if not line:
        return False
    if is_header_field(line):
        return False
    if re.fullmatch(r"\d{1,6}(?:\s+\d{1,6})*", line):
        return False
    if len(line.split()) < 3:
        return False
    if line.lower().startswith("district") and re.search(r"\d", line):
        return False
    return bool(re.search(r"[A-Za-z]", line))


def extract_college_header(text: str) -> tuple[str, str]:
    lines = [normalize_line(line) for line in text.splitlines() if normalize_line(line)]
    code_match = re.search(r"\b\d{4}\b", text)
    if not code_match:
        return "", ""

    college_code = code_match.group()
    boundary_index = len(lines)
    for i, line in enumerate(lines):
        if re.search(r"\b(Name of the Principal|Dean)\b", line, flags=re.IGNORECASE):
            boundary_index = i
            break

    code_line_index = next((i for i, line in enumerate(lines[:boundary_index]) if college_code in line), None)
    if code_line_index is None:
        return college_code, ""

    code_line = lines[code_line_index]
    
    previous_line = ""

    if code_line_index > 0:
        previous_line = normalize_line(lines[code_line_index - 1])

    remainder = normalize_line(code_line.replace(college_code, ""))
    
    # If the previous line looks like a college name and the current line
    # only contains "District XXXXX", use the previous line.
    if (
        previous_line
        and remainder.lower().startswith("district")
    ):
        return college_code, previous_line

    
    name_parts: list[str] = []

    if remainder and not is_header_field(remainder):
        if not (remainder.lower().startswith("district") and re.search(r"\d", remainder)):
            name_parts.append(remainder)

    for line in lines[code_line_index + 1 : boundary_index]:
        if is_header_field(line):
            break
        if is_name_candidate(line):
            name_parts.append(line)
            continue
        if name_parts and line.lower().startswith("district") and re.search(r"\d", line):
            name_parts.append(line)
            continue
        break

    prev_line_parts: list[str] = []
    for line in reversed(lines[:code_line_index]):
        if is_header_field(line):
            break
        if is_name_candidate(line) or (prev_line_parts and line.lower().startswith("district") and re.search(r"\d", line)):
            prev_line_parts.insert(0, line)
            continue
        break

    if prev_line_parts:
        prev_name = " ".join(prev_line_parts)

        # If the parser extracted only "District 636305",
        # use the previous line instead.
        if (
            not name_parts
            or (
                len(name_parts) == 1
                and name_parts[0].lower().startswith("district")
            )
        ):
            return college_code, prev_name

    # Otherwise use the normal extraction
    if name_parts:
        return college_code, " ".join(name_parts)

    return college_code, remainder

    

rows = []

with pdfplumber.open(pdf_path) as pdf:

    # Start from the college details section
    for page_no in range(230, len(pdf.pages)):

        page = pdf.pages[page_no]

        text = page.extract_text()

        if not text:
            continue

        college_code, college_name = extract_college_header(text)

        if college_code == "2639":
            print("=" * 60)
            print(text)
            print("=" * 60)

        if not college_code:
            continue

        tables = page.extract_tables()

        if len(tables) < 3:
            continue

        branch_table = tables[2]

        for row in branch_table[1:]:

            if len(row) < 6:
                continue

            rows.append([
                college_code,
                college_name,
                row[1],
                row[2],
                row[3],
                row[4],
                row[5]
            ])

with open(output_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "College Code",
        "College Name",
        "Branch Code",
        "Approved Intake",
        "Year Started",
        "NBA",
        "Accreditation Valid Upto"
    ])

    writer.writerows(rows)

print("Total Branches:", len(rows))
print("Saved to:", output_csv)