"""
Create colleges CSV from extracted PDF text.
"""

import re
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


def get_input_path() -> Path:
    """Return the path to the extracted text file."""
    return get_project_root() / "extracted_text.txt"


def get_output_path() -> Path:
    """Return the path to the target colleges CSV file."""
    return get_project_root() / "datasets" / "colleges.csv"


def is_page_marker(line: str) -> bool:
    """Return True when a line is a PDF page marker."""
    return bool(re.fullmatch(r"--- Page \d+ ---", line))


def is_roman_page_footer(line: str) -> bool:
    """Return True when a line contains only roman numerals used as a page footer."""
    return bool(re.fullmatch(r"[ivxlcdm]+", line, re.IGNORECASE))


def find_pincode(line: str) -> str | None:
    """Return the first 6-digit pincode found in a line, if any."""
    match = re.search(r"\b(\d{6})\b", line)
    return match.group(1) if match else None


def is_code_line(line: str) -> bool:
    """Return True when a line appears to contain the college code and serial number."""
    numbers = re.findall(r"\b\d+\b", line)
    if len(numbers) < 2:
        return False

    # Treat lines with at least two numeric groups as candidate code lines.
    # Exclude lines where the only numeric token is a 6-digit pincode.
    numeric_tokens = [n for n in numbers if len(n) != 6]
    return len(numeric_tokens) >= 2


def normalize_text(text: str) -> list[str]:
    """Normalize raw text into lines and drop page markers and footer markers."""
    normalized: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            normalized.append("")
            continue
        if is_page_marker(line) or is_roman_page_footer(line):
            continue
        normalized.append(line)

    return normalized


def sanitize_name_text(lines: list[str], pincode: str, district: str) -> str:
    """Build a clean college name from a list of lines."""
    text = " ".join(lines)
    text = text.replace(pincode, "")
    if district:
        text = text.replace(district, "")
    text = re.sub(r"\bDistrict\b", "", text)
    text = re.sub(r"\b\d{1,4}\b", "", text)
    text = re.sub(r"[,:;()]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_district(text: str, fallback_line: str | None = None) -> str:
    """Extract the district phrase from the text or fallback content."""
    match = re.search(r"([A-Za-z &\-\.']+District)", text)
    if match:
        return match.group(1).strip()

    if fallback_line:
        match = re.search(r"([A-Za-z &\-\.']+District)", fallback_line)
        if match:
            return match.group(1).strip()

    # If district is not explicitly present, use the last location segment before the pincode.
    fallback = re.sub(r"\b\d{6}\b", "", text).strip()
    if fallback:
        parts = [segment.strip() for segment in re.split(r",| - |/", fallback) if segment.strip()]
        if parts:
            return f"{parts[-1]} District"

    return ""


def extract_college_code(code_line: str) -> str | None:
    """Extract the college code from a line containing numeric tokens."""
    numbers = re.findall(r"\b\d+\b", code_line)
    codes = [n for n in numbers if len(n) != 6]
    if len(codes) >= 2:
        return codes[1]
    if codes:
        return codes[0]
    return None


def build_record(name_lines: list[str], code_line: str | None, pincode_line: str | None) -> dict[str, str] | None:
    """Build a record dictionary from the current entry lines."""
    if not code_line or not pincode_line:
        return None

    pincode = find_pincode(pincode_line) or ""
    college_code = extract_college_code(code_line) or ""

    # Include any trailing name text from a code line that contains both text and numbers.
    if not re.match(r"^\d+", code_line):
        name_lines.insert(0, code_line)
    else:
        text_after_code = re.sub(r"^\s*\d+\s+\d+\s*", "", code_line).strip()
        if text_after_code:
            name_lines.insert(0, text_after_code)

    raw_text = " ".join(name_lines)
    district = extract_district(raw_text, pincode_line)
    college_name = sanitize_name_text(name_lines, pincode, district)

    if not college_name:
        return None

    return {
        "College Code": college_code,
        "College Name": college_name,
        "District": district,
        "Pincode": pincode,
    }


def parse_college_entries(lines: list[str]) -> list[dict[str, str]]:
    """Parse all college entries from normalized text lines."""
    records: list[dict[str, str]] = []
    current_name_lines: list[str] = []
    current_code_line: str | None = None
    current_pincode_line: str | None = None

    def flush_current() -> None:
        nonlocal current_name_lines, current_code_line, current_pincode_line
        record = build_record(current_name_lines.copy(), current_code_line, current_pincode_line)
        if record:
            records.append(record)
        current_name_lines = []
        current_code_line = None
        current_pincode_line = None

    for line in lines:
        if not line:
            continue

        pincode = find_pincode(line)
        code_candidate = is_code_line(line)

        if code_candidate:
            # If the current entry already holds a code or pincode, finalize it before starting a new one.
            if current_code_line or current_pincode_line:
                flush_current()

            current_code_line = line
            if pincode:
                current_pincode_line = line
                flush_current()
            continue

        if pincode:
            current_pincode_line = line
            if current_code_line:
                flush_current()
            else:
                current_name_lines.append(line)
            continue

        current_name_lines.append(line)

    if current_code_line or current_pincode_line:
        flush_current()

    return records


def main() -> None:
    """Main entry point for creating the college CSV file."""
    input_path = get_input_path()
    output_path = get_output_path()

    raw_text = input_path.read_text(encoding="utf-8")
    lines = normalize_text(raw_text)
    records = parse_college_entries(lines)

    df = pd.DataFrame(records, columns=["College Code", "College Name", "District", "Pincode"])
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} college records to {output_path}")


if __name__ == "__main__":
    main()
