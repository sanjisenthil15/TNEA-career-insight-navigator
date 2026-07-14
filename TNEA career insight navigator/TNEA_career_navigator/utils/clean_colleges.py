"""
Clean extracted college records and save a normalized CSV.
"""

import re
from pathlib import Path

import pandas as pd


def get_input_path() -> Path:
    """Return the path to the raw colleges CSV file."""
    return Path(__file__).resolve().parent.parent / "datasets" / "colleges.csv"


def get_output_path() -> Path:
    """Return the path to the cleaned colleges CSV file."""
    return Path(__file__).resolve().parent.parent / "datasets" / "colleges_clean.csv"


def is_valid_college_code(code: str) -> bool:
    """Return True when the college code is a valid 4-digit engineering code."""
    return bool(re.fullmatch(r"\d{4}", code.strip()))


def contains_invalid_term(text: str) -> bool:
    """Return True if the text contains non-college information keywords."""
    pattern = re.compile(
        r"\b(hostel|transport|transportation|fee|fees|bank|accommodation|mess|boarding|canteen|lodging|bus|room|rooms|hostels?)\b",
        flags=re.IGNORECASE,
    )
    return bool(pattern.search(text or ""))


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe by validating codes, removing invalid rows, and dropping duplicates."""
    # Ensure the required columns exist.
    df = df.copy()
    df.columns = [col.strip() for col in df.columns]

    # Keep only the target columns, if available.
    target_columns = ["College Code", "College Name", "District", "Pincode"]
    df = df[[col for col in target_columns if col in df.columns]].copy()

    # Normalize whitespace in text columns.
    for col in ["College Name", "District"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": ""})

    # Convert College Code to string and remove invalid codes.
    df["College Code"] = df["College Code"].astype(str).str.strip()
    df = df[df["College Code"].apply(is_valid_college_code)]

    # Validate pincode format: exactly 6 digits.
    if "Pincode" in df.columns:
        df["Pincode"] = df["Pincode"].astype(str).str.replace(r"\s+", "", regex=True).str.strip()
        df = df[df["Pincode"].str.fullmatch(r"\d{6}").fillna(False)]

    # Remove rows with non-college information keywords in Name or District.
    df = df[~df["College Name"].apply(contains_invalid_term)]
    if "District" in df.columns:
        df = df[~df["District"].apply(contains_invalid_term)]

    # Drop exact duplicate college codes, keeping the first occurrence.
    df = df.drop_duplicates(subset=["College Code"], keep="first")

    # Keep only the requested columns in final output.
    df = df[["College Code", "College Name", "District", "Pincode"]]

    return df


def main() -> None:
    """Main function to load, clean, and save the college dataset."""
    input_path = get_input_path()
    output_path = get_output_path()

    raw_df = pd.read_csv(input_path)
    cleaned_df = normalize_dataframe(raw_df)
    cleaned_df.to_csv(output_path, index=False)

    print(f"Total colleges after cleaning: {len(cleaned_df)}")


if __name__ == "__main__":
    main()
