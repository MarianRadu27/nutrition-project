#!/usr/bin/env python3
"""Profile the NEVO dataset before importing it into the database.

This script does not modify the database. It only reads the source CSV files
and prints useful information about their structure and data quality.
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

NEVO_DIR = PROJECT_ROOT / "temp" / "EuropeNutrientsDBs" / "nevo"
NUTRIENTS_FILE = NEVO_DIR / "NEVO2025_v9.0_Nutrienten_Nutrients.csv"
MAIN_FILE = NEVO_DIR / "NEVO2025_v9.0.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a pipe-delimited NEVO CSV file into dictionaries."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter="|")
        return list(reader)
    
def read_nutrient_dictionary(path: Path) -> list[dict[str, str]]:
    """Read the NEVO nutrient dictionary file."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter="|")
        return list(reader)

def main() -> int:
    """Run a basic profile of the NEVO main file."""
    if not MAIN_FILE.exists():
        print(f"File not found: {MAIN_FILE}")
        return 1

    rows = read_rows(MAIN_FILE)

    print("NEVO main file profile")
    print("======================")
    print(f"File: {MAIN_FILE}")
    print(f"Rows: {len(rows)}")

    if not rows:
        print("No rows found.")
        return 0

    columns = list(rows[0].keys())
    print(f"Columns: {len(columns)}")
    print()
    print("First 15 columns:")
    for column in columns[:15]:
        print(f"- {column}")

    category_column = "Food group"
    categories = sorted({row[category_column] for row in rows if row[category_column]})

    print()
    print(f"Categories: {len(categories)}")
    print("First 20 categories:")
    for category in categories[:20]:
        print(f"- {category}")

    print()
    print("First 10 foods:")
    for row in rows[:10]:
        print(
            f"- {row['NEVO-code']} | "
            f"{row['Food group']} | "
            f"{row['Engelse naam/Food name']} | "
            f"{row['Hoeveelheid/Quantity']}"
        )

    quantity_column = "Hoeveelheid/Quantity"
    quantities = sorted({row[quantity_column] for row in rows if row[quantity_column]})

    print()
    print(f"Quantity values: {len(quantities)}")
    for quantity in quantities:
        print(f"- {quantity}")

    quantity_counts: dict[str, int] = {}
    for row in rows:
        quantity = row[quantity_column] or "(blank)"
        quantity_counts[quantity] = quantity_counts.get(quantity, 0) + 1

    print()
    print("Quantity counts:")
    for quantity, count in sorted(quantity_counts.items()):
        print(f"- {quantity}: {count}")
        
    main_nutrients = [
        "ENERCC (kcal)",
        "PROT (g)",
        "CHO (g)",
        "FAT (g)",
        "FIBT (g)",
    ]

    print()
    print("Main nutrient missing values:")
    for nutrient in main_nutrients:
        missing_count = sum(1 for row in rows if not row[nutrient])
        present_count = len(rows) - missing_count
        print(f"- {nutrient}: present={present_count}, missing={missing_count}")

    fiber_column = "FIBT (g)"

    print()
    print("Foods missing fiber:")
    for row in rows:
        if not row[fiber_column]:
            print(
                f"- {row['NEVO-code']} | "
                f"{row['Food group']} | "
                f"{row['Engelse naam/Food name']} | "
                f"{row['Hoeveelheid/Quantity']}"
            )

    code_column = "NEVO-code"
    seen_codes: set[str] = set()
    duplicate_codes: list[str] = []

    for row in rows:
        code = row[code_column]
        if code in seen_codes:
            duplicate_codes.append(code)
        else:
            seen_codes.add(code)

    print()
    print(f"Unique NEVO codes: {len(seen_codes)}")
    print(f"Duplicate NEVO codes: {len(duplicate_codes)}")

    if duplicate_codes:
        print("First duplicate codes:")
        for code in duplicate_codes[:20]:
            print(f"- {code}")


    first_nutrient_column = "ENERCJ (kJ)"
    first_nutrient_index = columns.index(first_nutrient_column)

    metadata_columns = columns[:first_nutrient_index]
    nutrient_columns = columns[first_nutrient_index:]

    print()
    print(f"Metadata columns: {len(metadata_columns)}")
    print(f"Nutrient columns: {len(nutrient_columns)}")
    print(f"Total {len(metadata_columns + nutrient_columns)}")
    print("First 20 nutrient columns:")
    for column in nutrient_columns[:20]:
        print(f"- {column}")
                    
    nutrient_dictionary = read_nutrient_dictionary(NUTRIENTS_FILE)

    print()
    print("Nutrient dictionary profile")
    print("===========================")
    print(f"File: {NUTRIENTS_FILE}")
    print(f"Rows: {len(nutrient_dictionary)}")

    print("First 10 nutrient definitions:")
    for row in nutrient_dictionary[:10]:
        print(
            f"- {row['Nutrient-code']} | "
            f"{row['Component']} | "
            f"{row['Eenheid/Unit']}"
        )

    dictionary_codes = {
        row["Nutrient-code"].strip()
        for row in nutrient_dictionary
        if row["Nutrient-code"].strip()
    }

    main_nutrient_codes = {
        column.split(" (", 1)[0].strip()
        for column in nutrient_columns
    }

    missing_from_dictionary = sorted(main_nutrient_codes - dictionary_codes)
    dictionary_not_in_main = sorted(dictionary_codes - main_nutrient_codes)

    print()
    print("Nutrient code comparison")
    print("========================")
    print(f"Codes in main file: {len(main_nutrient_codes)}")
    print(f"Codes in dictionary: {len(dictionary_codes)}")
    print(f"Main codes missing from dictionary: {len(missing_from_dictionary)}")
    for code in missing_from_dictionary[:20]:
        print(f"- {code}")

    print(f"Dictionary codes not in main file: {len(dictionary_not_in_main)}")
    for code in dictionary_not_in_main[:20]:
        print(f"- {code}")
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
