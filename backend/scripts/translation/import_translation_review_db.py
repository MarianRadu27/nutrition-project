from __future__ import annotations

"""Load reviewed Romanian translations from Excel into MySQL."""

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db import get_connection  # noqa: E402


DEFAULT_INPUT = PROJECT_ROOT / "backend" / "data" / "translation_review_with_suggestions.xlsx"


@dataclass
class ImportStats:
    selected_rows: int = 0
    skipped_rows: int = 0
    categories_updated: int = 0
    foods_updated: int = 0
    food_descriptions_updated: int = 0
    missing_keys: int = 0


def is_blank(value: Any) -> bool:
    """Treat pandas missing values and empty strings as blank."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def clean_text(value: Any) -> str:
    """Convert Excel values to clean strings."""
    if is_blank(value):
        return ""
    return str(value).strip()


def clean_int(value: Any) -> int | None:
    """Read integer identifiers that may come from Excel as floats."""
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return None

    text = clean_text(value).replace(",", "")
    if text.endswith(".0"):
        text = text[:-2]
    if text.isdigit():
        return int(text)
    return None


def status_is_allowed(row_status: Any, allowed_statuses: set[str]) -> bool:
    """Compare statuses case-insensitively."""
    return clean_text(row_status).lower() in allowed_statuses


def update_category(cursor: Any, entity_id: int, translation: str) -> int:
    cursor.execute(
        "UPDATE categories SET name_ro = %s WHERE id = %s",
        (translation, entity_id),
    )
    return int(cursor.rowcount)


def update_food_group(cursor: Any, entity_id: int, translation: str) -> int:
    cursor.execute(
        "UPDATE subcategories SET name_ro = %s WHERE id = %s",
        (translation, entity_id),
    )
    return int(cursor.rowcount)


def update_food_description(
    cursor: Any, entity_id: int, da_code: int | None, translation: str
) -> int:
    """Update by id and DA code together when DA code is available."""
    if da_code is None:
        cursor.execute(
            "UPDATE foods SET food_description_ro = %s WHERE id = %s",
            (translation, entity_id),
        )
    else:
        cursor.execute(
            """
            UPDATE foods
            SET food_description_ro = %s
            WHERE id = %s AND da_code = %s
            """,
            (translation, entity_id, da_code),
        )
    return int(cursor.rowcount)


def import_sheet(
    *,
    cursor: Any,
    sheet_name: str,
    dataframe: pd.DataFrame,
    allowed_statuses: set[str],
    stats: ImportStats,
    limit: int | None,
) -> bool:
    """Import one review sheet. Returns True when the optional limit is reached."""
    for _, row in dataframe.iterrows():
        if limit is not None and stats.selected_rows >= limit:
            return True

        # Statuses let us import only reviewed rows, or include needs_review on purpose.
        if not status_is_allowed(row.get("status"), allowed_statuses):
            stats.skipped_rows += 1
            continue

        translation = clean_text(row.get("suggested_ro"))
        entity_type = clean_text(row.get("entity_type"))
        entity_id = clean_int(row.get("entity_id"))
        da_code = clean_int(row.get("da_code"))

        if not translation or entity_id is None:
            stats.skipped_rows += 1
            continue

        stats.selected_rows += 1

        if entity_type == "category" or sheet_name == "categories":
            changed = update_category(cursor, entity_id, translation)
            stats.categories_updated += changed
        elif entity_type == "food" or sheet_name == "foods":
            changed = update_food_group(cursor, entity_id, translation)
            stats.foods_updated += changed
        elif entity_type == "food_description" or sheet_name == "food_descriptions":
            changed = update_food_description(cursor, entity_id, da_code, translation)
            stats.food_descriptions_updated += changed
        else:
            changed = 0

        if changed == 0:
            stats.missing_keys += 1

    return False


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import approved Romanian translations from the review workbook into MySQL."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Review Excel file.")
    parser.add_argument(
        "--statuses",
        nargs="+",
        default=["approved"],
        help="Statuses allowed for import. Example: --statuses approved needs_review",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit changes to MySQL. Without this, the transaction is rolled back.",
    )
    parser.add_argument("--limit", type=int, help="Optional max rows to import.")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (PROJECT_ROOT / input_path).resolve()

    if not input_path.exists():
        print(f"ERROR: Review file not found: {input_path}")
        return 1

    allowed_statuses = {status.lower() for status in args.statuses}
    workbook = pd.read_excel(input_path, sheet_name=None, dtype=object)
    stats = ImportStats()

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for sheet_name in ["categories", "foods", "food_descriptions"]:
                if sheet_name not in workbook:
                    continue
                stop = import_sheet(
                    cursor=cursor,
                    sheet_name=sheet_name,
                    dataframe=workbook[sheet_name],
                    allowed_statuses=allowed_statuses,
                    stats=stats,
                    limit=args.limit,
                )
                if stop:
                    break

        if args.commit:
            connection.commit()
            print("Commit complete.")
        else:
            connection.rollback()
            print("Dry-run complete: rolled back transaction.")
    except Exception as exc:
        connection.rollback()
        print(f"ERROR: Import failed, transaction rolled back: {exc}")
        return 1
    finally:
        connection.close()

    print("")
    print("Summary:")
    print(f"  statuses:                  {', '.join(sorted(allowed_statuses))}")
    print(f"  selected rows:             {stats.selected_rows}")
    print(f"  skipped rows:              {stats.skipped_rows}")
    print(f"  categories updated:        {stats.categories_updated}")
    print(f"  foods updated:             {stats.foods_updated}")
    print(f"  food descriptions updated: {stats.food_descriptions_updated}")
    print(f"  unchanged/missing rows:    {stats.missing_keys}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
