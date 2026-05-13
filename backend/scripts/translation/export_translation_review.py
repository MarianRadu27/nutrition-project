from __future__ import annotations

"""Export DB text into an Excel review workbook for translation.

The review workbook is a staging file: humans or tools fill suggested_ro there,
and a later import step writes approved rows back into MySQL.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db import get_connection  # noqa: E402


DEFAULT_OUTPUT = PROJECT_ROOT / "backend" / "data" / "translation_review.xlsx"


def translation_status(current_ro: str | None) -> str:
    """Mark each row so the review file is easy to filter in Excel."""
    if current_ro and current_ro.strip():
        return "already_translated"
    return "needs_translation"


def fetch_categories(cursor: Any, only_missing: bool) -> list[dict[str, Any]]:
    """Export Category rows."""
    sql = """
        SELECT
            id AS entity_id,
            name AS english_text,
            name_ro AS current_ro
        FROM categories
    """
    params: list[Any] = []
    if only_missing:
        sql += " WHERE name_ro IS NULL OR name_ro = ''"
    sql += " ORDER BY name ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    return [
        {
            "entity_type": "category",
            "entity_id": row["entity_id"],
            "da_code": None,
            "category_id": row["entity_id"],
            "category_en": row["english_text"],
            "food_id": None,
            "food_en": None,
            "english_text": row["english_text"],
            "current_ro": row["current_ro"],
            "suggested_ro": "",
            "status": translation_status(row["current_ro"]),
            "notes": "",
        }
        for row in rows
    ]


def fetch_food_groups(cursor: Any, only_missing: bool) -> list[dict[str, Any]]:
    """Export Food group rows, stored as subcategories in the DB."""
    sql = """
        SELECT
            s.id AS entity_id,
            s.category_id,
            c.name AS category_en,
            s.name AS english_text,
            s.name_ro AS current_ro
        FROM subcategories s
        JOIN categories c ON c.id = s.category_id
    """
    params: list[Any] = []
    if only_missing:
        sql += " WHERE s.name_ro IS NULL OR s.name_ro = ''"
    sql += " ORDER BY c.name ASC, s.name ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    return [
        {
            "entity_type": "food",
            "entity_id": row["entity_id"],
            "da_code": None,
            "category_id": row["category_id"],
            "category_en": row["category_en"],
            "food_id": row["entity_id"],
            "food_en": row["english_text"],
            "english_text": row["english_text"],
            "current_ro": row["current_ro"],
            "suggested_ro": "",
            "status": translation_status(row["current_ro"]),
            "notes": "",
        }
        for row in rows
    ]


def fetch_food_descriptions(cursor: Any, only_missing: bool) -> list[dict[str, Any]]:
    """Export Food Description rows with category/food context for translators."""
    sql = """
        SELECT
            f.id AS entity_id,
            f.da_code,
            s.category_id,
            c.name AS category_en,
            f.subcategory_id AS food_id,
            s.name AS food_en,
            f.food_description AS english_text,
            f.food_description_ro AS current_ro
        FROM foods f
        LEFT JOIN subcategories s ON s.id = f.subcategory_id
        LEFT JOIN categories c ON c.id = s.category_id
    """
    params: list[Any] = []
    if only_missing:
        sql += " WHERE f.food_description_ro IS NULL OR f.food_description_ro = ''"
    sql += " ORDER BY c.name ASC, s.name ASC, f.food_description ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    return [
        {
            "entity_type": "food_description",
            "entity_id": row["entity_id"],
            "da_code": row["da_code"],
            "category_id": row["category_id"],
            "category_en": row["category_en"],
            "food_id": row["food_id"],
            "food_en": row["food_en"],
            "english_text": row["english_text"],
            "current_ro": row["current_ro"],
            "suggested_ro": "",
            "status": translation_status(row["current_ro"]),
            "notes": "",
        }
        for row in rows
    ]


def write_review_file(
    output_path: Path,
    categories: list[dict[str, Any]],
    food_groups: list[dict[str, Any]],
    food_descriptions: list[dict[str, Any]],
) -> None:
    """Write separate Excel sheets so each translation type is easy to review."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame(categories).to_excel(writer, sheet_name="categories", index=False)
        pd.DataFrame(food_groups).to_excel(writer, sheet_name="foods", index=False)
        pd.DataFrame(food_descriptions).to_excel(
            writer, sheet_name="food_descriptions", index=False
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export category, food, and food description texts for Romanian review."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Excel review file to create.",
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Export only rows that do not already have Romanian text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (PROJECT_ROOT / output_path).resolve()

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            categories = fetch_categories(cursor, args.only_missing)
            food_groups = fetch_food_groups(cursor, args.only_missing)
            food_descriptions = fetch_food_descriptions(cursor, args.only_missing)
    finally:
        connection.close()

    write_review_file(
        output_path=output_path,
        categories=categories,
        food_groups=food_groups,
        food_descriptions=food_descriptions,
    )

    print(f"Review file created: {output_path}")
    print(f"Categories:        {len(categories)}")
    print(f"Foods:             {len(food_groups)}")
    print(f"Food descriptions: {len(food_descriptions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
