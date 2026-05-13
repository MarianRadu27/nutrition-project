from __future__ import annotations

"""Create small CSV batches that can be translated with ChatGPT in the browser."""

import argparse
import csv
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = PROJECT_ROOT / "backend" / "data" / "translation_review.xlsx"
DEFAULT_OUTPUT = PROJECT_ROOT / "backend" / "data" / "translation_chatgpt_batch.csv"


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
    """Convert Excel values to clean strings."""
    if is_blank(value):
        return ""
    return str(value).strip()


def should_export(row: pd.Series) -> bool:
    """Export only rows that still need a Romanian suggestion."""
    english_text = clean_text(row.get("english_text"))
    current_ro = clean_text(row.get("current_ro"))
    suggested_ro = clean_text(row.get("suggested_ro"))

    return bool(english_text and not current_ro and not suggested_ro)


def build_context(row: pd.Series) -> str:
    """Give ChatGPT useful context without making the CSV too wide."""
    entity_type = clean_text(row.get("entity_type"))
    category = clean_text(row.get("category_en"))
    food = clean_text(row.get("food_en"))

    if entity_type == "food_description":
        return f"Category: {category}; Food: {food}"
    if entity_type == "food":
        return f"Category: {category}"
    return ""


def export_batch(
    *,
    input_path: Path,
    output_path: Path,
    sheet_name: str,
    limit: int,
    offset: int,
) -> int:
    """Export a stable CSV batch that can be translated outside the project."""
    dataframe = pd.read_excel(input_path, sheet_name=sheet_name, dtype=object)

    selected_rows: list[dict[str, str]] = []
    skipped = 0

    for row_index, row in dataframe.iterrows():
        if not should_export(row):
            continue

        if skipped < offset:
            skipped += 1
            continue

        # row_key is the stable link back to the exact Excel sheet and row index.
        selected_rows.append(
            {
                "row_key": f"{sheet_name}:{row_index}",
                "entity_type": clean_text(row.get("entity_type")),
                "context": build_context(row),
                "english_text": clean_text(row.get("english_text")),
                "romanian_text": "",
            }
        )

        if len(selected_rows) >= limit:
            break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "row_key",
                "entity_type",
                "context",
                "english_text",
                "romanian_text",
            ],
        )
        writer.writeheader()
        writer.writerows(selected_rows)

    return len(selected_rows)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a CSV batch that can be translated with ChatGPT in the browser."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Review Excel file.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="CSV batch file to create.",
    )
    parser.add_argument(
        "--sheet",
        default="food_descriptions",
        choices=["categories", "foods", "food_descriptions"],
        help="Review sheet to export.",
    )
    parser.add_argument("--limit", type=int, default=50, help="Rows to export.")
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip this many still-untranslated rows before exporting.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    if not input_path.exists():
        print(f"ERROR: Review file not found: {input_path}")
        return 1

    exported_count = export_batch(
        input_path=input_path,
        output_path=output_path,
        sheet_name=args.sheet,
        limit=args.limit,
        offset=args.offset,
    )

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Sheet: {args.sheet}")
    print(f"Rows exported: {exported_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
