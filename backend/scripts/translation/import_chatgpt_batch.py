from __future__ import annotations

"""Merge a translated ChatGPT CSV batch back into the review workbook."""

import argparse
import csv
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REVIEW = PROJECT_ROOT / "backend" / "data" / "translation_review.xlsx"
DEFAULT_BATCH = PROJECT_ROOT / "backend" / "data" / "translation_chatgpt_batch.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "backend" / "data" / "translation_review_with_suggestions.xlsx"

REVIEW_COLUMNS = [
    "entity_type",
    "entity_id",
    "da_code",
    "category_id",
    "category_en",
    "food_id",
    "food_en",
    "english_text",
    "current_ro",
    "suggested_ro",
    "status",
    "notes",
]


def resolve_path(path_text: str) -> Path:
    """Resolve paths from the project root unless an absolute path is provided."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def is_blank(value: Any) -> bool:
    """Treat pandas missing values and empty strings as blank."""
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def clean_text(value: Any) -> str:
    """Convert CSV and Excel values to clean strings."""
    if is_blank(value):
        return ""
    return str(value).strip()


def read_review_workbook(review_path: Path) -> dict[str, pd.DataFrame]:
    """Read the review workbook and keep editable columns as text-friendly objects."""
    sheets = pd.read_excel(review_path, sheet_name=None, dtype=object)
    for dataframe in sheets.values():
        for column in REVIEW_COLUMNS:
            if column not in dataframe.columns:
                dataframe[column] = ""
            else:
                dataframe[column] = dataframe[column].astype("object")
    return sheets


def read_batch_translations(batch_path: Path) -> dict[str, str]:
    """Read translated CSV rows keyed by stable row_key."""
    translations: dict[str, str] = {}

    with batch_path.open("r", newline="", encoding="utf-8-sig") as file:
        sample = file.read(4096)
        file.seek(0)

        # ChatGPT/Excel may return comma-separated, tab-separated, or semicolon CSV.
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(file, dialect=dialect)
        required_columns = {"row_key", "romanian_text"}
        missing_columns = required_columns - set(reader.fieldnames or [])
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise RuntimeError(f"Batch file missing columns: {missing_text}")

        for row in reader:
            row_key = clean_text(row.get("row_key"))
            romanian_text = clean_text(row.get("romanian_text"))
            if not row_key or not romanian_text:
                continue
            translations[row_key] = romanian_text

    return translations


def apply_batch_translations(
    sheets: dict[str, pd.DataFrame],
    translations_by_key: dict[str, str],
    approve: bool,
) -> tuple[int, list[str]]:
    """Apply CSV translations to suggested_ro using row_key."""
    applied = 0
    missing_keys: list[str] = []

    for row_key, romanian_text in translations_by_key.items():
        if ":" not in row_key:
            missing_keys.append(row_key)
            continue

        # row_key has the shape "sheet_name:zero_based_row_index".
        sheet_name, row_index_text = row_key.split(":", 1)
        if sheet_name not in sheets or not row_index_text.isdigit():
            missing_keys.append(row_key)
            continue

        row_index = int(row_index_text)
        dataframe = sheets[sheet_name]
        if row_index not in dataframe.index:
            missing_keys.append(row_key)
            continue

        dataframe.at[row_index, "suggested_ro"] = romanian_text
        dataframe.at[row_index, "status"] = "approved" if approve else "needs_review"
        applied += 1

    return applied, missing_keys


def write_review_workbook(output_path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    """Save all sheets to a new review workbook."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, dataframe in sheets.items():
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a translated ChatGPT CSV batch back into the review workbook."
    )
    parser.add_argument("--review", default=str(DEFAULT_REVIEW), help="Review Excel file.")
    parser.add_argument("--batch", default=str(DEFAULT_BATCH), help="Translated CSV batch.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Review Excel file to create.",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Mark imported translations as approved instead of needs_review.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    review_path = resolve_path(args.review)
    batch_path = resolve_path(args.batch)
    output_path = resolve_path(args.output)

    if not review_path.exists():
        print(f"ERROR: Review file not found: {review_path}")
        return 1
    if not batch_path.exists():
        print(f"ERROR: Batch file not found: {batch_path}")
        return 1

    sheets = read_review_workbook(review_path)
    translations_by_key = read_batch_translations(batch_path)
    applied, missing_keys = apply_batch_translations(
        sheets=sheets,
        translations_by_key=translations_by_key,
        approve=args.approve,
    )
    write_review_workbook(output_path, sheets)

    print(f"Review input: {review_path}")
    print(f"Batch input:  {batch_path}")
    print(f"Output:       {output_path}")
    print(f"Translations read:    {len(translations_by_key)}")
    print(f"Translations applied: {applied}")
    print(f"Missing keys:         {len(missing_keys)}")
    if missing_keys:
        print("First missing keys:")
        for row_key in missing_keys[:10]:
            print(f"  {row_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
