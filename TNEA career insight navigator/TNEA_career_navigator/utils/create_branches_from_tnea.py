"""
Create branches.csv from the official TNEA Cutoff Portal.

This script reads college codes from datasets/colleges_clean.csv, queries the portal for
branch listings, and writes the consolidated branch data to datasets/branches.csv.
"""

import re
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# The portal URL template should be updated if the official endpoint changes.
# This current value is a best-effort placeholder for the TNEA cutoff portal.
TNEA_PORTAL_URL_TEMPLATE = (
    "https://tneaonline.org/CutOff/CollegeWiseCutoff?collegecode={college_code}"
)

FORBIDDEN_TERMS = re.compile(
    r"\b(principal|bank|dean|hostel|transport|fee|fees|address|a/c|list of course code|course code|accommodation|mess|room|electricity|caution|establishment|admission|website|email|phone|antiphone|distance|nearest|railway|taluk|minority|status|autonomous|pincode)\b",
    flags=re.IGNORECASE,
)

BRANCH_CODE_PATTERN = re.compile(r"^[A-Z]{1,4}(?:/[A-Z]{1,4})?$")
INTAKE_PATTERN = re.compile(r"^\d{1,4}$")


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


def get_college_codes_path() -> Path:
    """Return the path to the cleaned colleges CSV file."""
    return get_project_root() / "datasets" / "colleges_clean.csv"


def get_output_path() -> Path:
    """Return the path to the generated branches CSV file."""
    return get_project_root() / "datasets" / "branches.csv"


def load_college_codes() -> pd.DataFrame:
    """Load college codes and college names from the cleaned college CSV."""
    csv_path = get_college_codes_path()
    df = pd.read_csv(csv_path, dtype={"College Code": str, "College Name": str})
    df["College Code"] = df["College Code"].str.strip()
    df["College Name"] = df["College Name"].astype(str).str.strip()
    return df


def build_college_url(college_code: str) -> str:
    """Create the portal URL for a given college code."""
    return TNEA_PORTAL_URL_TEMPLATE.format(college_code=college_code)


def clean_text(value: str) -> str:
    """Normalize whitespace and strip text."""
    return re.sub(r"\s+", " ", value or "").strip()


def row_contains_forbidden_terms(row_text: str) -> bool:
    """Return True when a row contains unrelated portal text."""
    return bool(FORBIDDEN_TERMS.search(row_text))


def parse_branch_row(cells: list[str]) -> tuple[str, str, str] | None:
    """Try to extract branch code, branch name, and intake from a row's cells."""
    normalized = [clean_text(cell) for cell in cells if clean_text(cell)]
    if len(normalized) < 2:
        return None

    # A typical row contains a branch code, branch name, and numeric intake.
    branch_code = None
    approved_intake = ""
    branch_name_parts: list[str] = []

    for index, cell in enumerate(normalized):
        if BRANCH_CODE_PATTERN.fullmatch(cell):
            branch_code = cell
            branch_name_parts = normalized[index + 1 :]
            break

    if not branch_code:
        return None

    if branch_name_parts:
        for part in reversed(branch_name_parts):
            if INTAKE_PATTERN.fullmatch(part):
                approved_intake = part
                branch_name_parts = branch_name_parts[:-1]
                break

    branch_name = " ".join(branch_name_parts).strip()
    if not branch_name or not approved_intake:
        return None

    return branch_code, branch_name, approved_intake


def locate_branch_tables(soup: BeautifulSoup) -> list:
    """Locate tables that likely contain branch rows."""
    candidate_tables = []
    for table in soup.find_all("table"):
        header_text = " ".join(th.get_text(separator=" ", strip=True) for th in table.find_all("th"))
        if re.search(r"branch\s*code|branch\s*name|intake", header_text, flags=re.IGNORECASE):
            candidate_tables.append(table)
    return candidate_tables


def parse_table_rows(table, college_code: str, college_name: str) -> list[dict[str, str]]:
    """Parse a single HTML table and extract branch rows."""
    records = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["td", "th"])]
        row_text = " ".join(cells)
        if row_contains_forbidden_terms(row_text):
            continue
        parsed = parse_branch_row(cells)
        if parsed:
            branch_code, branch_name, approved_intake = parsed
            records.append(
                {
                    "College Code": college_code,
                    "College Name": college_name,
                    "Branch Code": branch_code,
                    "Branch Name": branch_name,
                    "Approved Intake": approved_intake,
                }
            )
    return records


def extract_branch_records_from_html(html: str, college_code: str, college_name: str) -> list[dict[str, str]]:
    """Extract branch records from HTML content returned by the portal."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, str]] = []

    tables = locate_branch_tables(soup)
    for table in tables:
        records.extend(parse_table_rows(table, college_code, college_name))

    # If no candidate table was found, attempt a broader scan of all rows.
    if not records:
        for tr in soup.find_all("tr"):
            cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["td", "th"])]
            row_text = " ".join(cells)
            if row_contains_forbidden_terms(row_text):
                continue
            parsed = parse_branch_row(cells)
            if parsed:
                branch_code, branch_name, approved_intake = parsed
                records.append(
                    {
                        "College Code": college_code,
                        "College Name": college_name,
                        "Branch Code": branch_code,
                        "Branch Name": branch_name,
                        "Approved Intake": approved_intake,
                    }
                )
    return records


def fetch_college_branch_records(college_code: str, college_name: str) -> list[dict[str, str]]:
    """Fetch branch records for a single college from the portal."""
    url = build_college_url(college_code)
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return extract_branch_records_from_html(response.text, college_code, college_name)


def main() -> None:
    """Main entry point to generate the branches CSV from the TNEA portal."""
    college_df = load_college_codes()
    output_path = get_output_path()

    branch_records: list[dict[str, str]] = []

    total = len(college_df)
    for index, row in college_df.iterrows():
        college_code = str(row["College Code"]).strip()
        college_name = str(row["College Name"]).strip()
        print(f"Processing {index + 1} of {total}")

        try:
            records = fetch_college_branch_records(college_code, college_name)
            branch_records.extend(records)
        except Exception as exc:
            print(f"Skipping college {college_code}: {exc}")
            continue

    df = pd.DataFrame(
        branch_records,
        columns=["College Code", "College Name", "Branch Code", "Branch Name", "Approved Intake"],
    )
    df.to_csv(output_path, index=False)

    print(f"Wrote {len(df)} branch records to {output_path}")


if __name__ == "__main__":
    main()
