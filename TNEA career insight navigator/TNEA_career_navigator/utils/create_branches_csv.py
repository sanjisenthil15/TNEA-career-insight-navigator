"""
Create a branches CSV from extracted PDF text.
"""

import re
from collections import deque
from pathlib import Path

import pandas as pd


FORBIDDEN_TERMS = re.compile(
    r"\b(principal|bank|dean|hostel|transport|fees?|address|a/c|list of course code|course code|accommodation|mess|room|electricity|caution|establishment|admission|website|email|phone|antiphone|distance|nearest|railway|taluk|minority|status|autonomous|pincode)\b",
    flags=re.IGNORECASE,
)


def get_input_path() -> Path:
    """Return the path to the extracted text source file."""
    return Path(__file__).resolve().parent.parent / "extracted_text.txt"


def get_colleges_path() -> Path:
    """Return the path to the cleaned colleges CSV file."""
    return Path(__file__).resolve().parent.parent / "datasets" / "colleges_clean.csv"


def get_output_path() -> Path:
    """Return the path to the generated branches CSV file."""
    return Path(__file__).resolve().parent.parent / "datasets" / "branches.csv"


def is_page_marker(line: str) -> bool:
    """Return True if the line is a page marker inserted during extraction."""
    return bool(re.fullmatch(r"--- Page \d+ ---", line))


def is_roman_footer(line: str) -> bool:
    """Return True if the line contains only roman numerals used as a footer."""
    return bool(re.fullmatch(r"[ivxlcdm]+", line, re.IGNORECASE))


def clean_lines(lines: list[str]) -> list[str]:
    """Clean raw text lines by removing empty lines and obvious page artifacts."""
    cleaned: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or is_page_marker(line) or is_roman_footer(line):
            continue
        cleaned.append(line)
    return cleaned


def normalize_for_match(text: str) -> str:
    """Create a compact text form for text matching."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def parse_branch_code_map(lines: list[str]) -> dict[str, str]:
    """Parse the general branch code table at the start of the document."""
    branch_map: dict[str, str] = {}
    section_started = False
    current_code: str | None = None
    current_name_parts: list[str] = []

    for line in lines:
        if not section_started:
            if line.startswith("3. LIST OF COURSE CODE AND ITS BRANCHES"):
                section_started = True
            continue

        # The branch code table ends before the college detail section begins.
        if line.startswith("University Departments of"):
            break

        match = re.match(r"^([A-Z]{1,4}(?:/[A-Z]{1,4})?)\s+(.+)$", line)
        if match:
            if current_code:
                branch_map[current_code] = " ".join(current_name_parts).strip()
            current_code = match.group(1).strip()
            current_name_parts = [match.group(2).strip()]
            continue

        if re.fullmatch(r"[A-Z]{1,4}(?:/[A-Z]{1,4})?", line):
            if current_code:
                branch_map[current_code] = " ".join(current_name_parts).strip()
            current_code = line.strip()
            current_name_parts = []
            continue

        if current_code:
            current_name_parts.append(line.strip())

    if current_code:
        branch_map[current_code] = " ".join(current_name_parts).strip()

    return branch_map


def load_college_lookup() -> list[tuple[str, str]]:
    """Load college names and codes from the cleaned colleges CSV."""
    colleges_path = get_colleges_path()
    if not colleges_path.exists():
        return []

    df = pd.read_csv(colleges_path)
    lookup: list[tuple[str, str]] = []
    for _, row in df.iterrows():
        name = str(row.get("College Name", "")).strip()
        code = str(row.get("College Code", "")).strip()
        if name and re.fullmatch(r"\d{4}", code):
            lookup.append((name, code))
    return lookup


def find_college_in_context(context_lines: deque[str], college_lookup: list[tuple[str, str]]) -> tuple[str, str] | None:
    """Find the college name and code nearest to a branch row using a recent context window."""
    combined_context = " ".join(list(context_lines))
    normalized_context = normalize_for_match(combined_context)

    for name, code in college_lookup:
        if normalize_for_match(name) in normalized_context:
            return name, code

    return None


def is_branch_row(line: str) -> tuple[str, str] | None:
    """Return branch code and approved intake when a line is a real branch row."""
    if FORBIDDEN_TERMS.search(line):
        return None

    match = re.match(r"^\s*\d+\s+([A-Z]{1,4}(?:/[A-Z]{1,4})?)\s+(\d{1,3})\b", line)
    if not match:
        return None

    branch_code = match.group(1).strip()
    approved_intake = match.group(2).strip()
    return branch_code, approved_intake


def parse_branch_records(lines: list[str], branch_map: dict[str, str], college_lookup: list[tuple[str, str]]) -> list[dict[str, str]]:
    """Extract branch records from the college detail sections only."""
    records: list[dict[str, str]] = []
    context_lines: deque[str] = deque(maxlen=80)
    started = False

    for line in lines:
        if not started:
            if line.startswith("University Departments of"):
                started = True
            continue

        # Skip line noise such as principal, bank, hostel, transport, fees, and address information.
        if not line or FORBIDDEN_TERMS.search(line):
            context_lines.append(line)
            continue

        branch_info = is_branch_row(line)
        if branch_info:
            branch_code, approved_intake = branch_info
            branch_name = branch_map.get(branch_code, "")
            college_match = find_college_in_context(context_lines, college_lookup)
            if college_match and branch_name:
                college_name, college_code = college_match
                records.append(
                    {
                        "College Code": college_code,
                        "College Name": college_name,
                        "Branch Code": branch_code,
                        "Branch Name": branch_name,
                        "Approved Intake": approved_intake,
                    }
                )

        context_lines.append(line)

    return records


def main() -> None:
    """Main function to parse and save branch records."""
    input_path = get_input_path()
    output_path = get_output_path()

    raw_text = input_path.read_text(encoding="utf-8")
    lines = clean_lines(raw_text.splitlines())

    branch_map = parse_branch_code_map(lines)
    college_lookup = load_college_lookup()
    branch_records = parse_branch_records(lines, branch_map, college_lookup)

    df = pd.DataFrame(
        branch_records,
        columns=["College Code", "College Name", "Branch Code", "Branch Name", "Approved Intake"],
    )
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} branch records to {output_path}")


if __name__ == "__main__":
    main()
