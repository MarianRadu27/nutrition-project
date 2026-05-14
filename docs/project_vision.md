# Project Vision

## Purpose

This project started as a practical way to learn data engineering by working with real nutrition data.

The goal is to build a public nutrition website that combines:

- a searchable food database;
- a meal nutrition calculator;
- multiple public food composition data sources;
- clear source attribution and disclaimers;
- a professional presentation page for a nutrition specialist.

The project is also intended as a portfolio project for data engineering and data analysis roles. It should show practical skills in data ingestion, cleaning, normalization, database design, API development, and frontend presentation.

## Product Vision

The public website should be useful for people who want quick nutrition estimates without manually typing calories, protein, carbohydrates, fat, fiber, and other nutrients.

Users should be able to:

- search for foods;
- select foods from trusted nutrition databases;
- enter grams or portions;
- calculate meal totals automatically;
- compare data from different nutrition sources;
- understand where the data comes from;
- read clear disclaimers about missing values and estimation limits;
- discover the nutrition specialist behind the website.

The website can also support professional visibility for the nutritionist by offering a useful free tool while clearly presenting her profile, services, and contact information.

## Data Engineering Vision

The long-term data goal is not just to store one spreadsheet. The goal is to build a small nutrition data platform.

The platform should be able to ingest several public data sources, such as:

- the current Appendix H / USDA-and-manufacturer-based local food table;
- NEVO from the Netherlands;
- ANSES / Ciqual from France;
- BLS from Germany;
- Open Food Facts for branded products.

Each source has its own structure, codes, names, nutrients, units, missing values, and license requirements. The project should preserve those differences instead of hiding them too early.

## Recommended Data Model Direction

Future sources should be added to the same MySQL database, but not forced directly into the current `foods` table.

A better long-term structure is:

```text
data_sources
canonical_foods
source_foods
nutrients
source_food_nutrient_values
food_matches
```

### data_sources

Stores one row per external source.

Example:

```text
ANSES - Ciqual 2025
NEVO - NEVO 2025
BLS - BLS 4.0 2025
OFF - Open Food Facts
```

This makes the system extensible. A new source can be added later by inserting a new row in `data_sources` and importing its foods into the same normalized structure.

### source_foods

Stores the original food rows from each source.

This table should preserve:

- source name;
- source food code;
- original food name;
- English food name when available;
- source category fields;
- serving basis, usually `per_100g`;
- metadata needed for traceability.

The source rows should not be deleted just because another source has a similar food. They are evidence of where the values came from.

### nutrients

Stores normalized nutrient definitions.

For example:

```text
kcal
protein_g
carbs_g
fat_g
fiber_g
calcium_mg
vitamin_c_mg
```

This is where source-specific nutrient codes can be mapped to common internal names.

Example:

```text
NEVO PROT      -> protein_g
BLS PROT625    -> protein_g
ANSES Protein  -> protein_g
```

### source_food_nutrient_values

Stores nutrient values for each source food.

This table should preserve:

- source food id;
- nutrient id;
- value;
- unit;
- basis, such as `per_100g`;
- source reference when available;
- missing value status when needed.

This is better than creating hundreds of nutrient columns directly on one food table.

### canonical_foods

Stores the user-facing food identity.

For example:

```text
Banana, raw
Apple, raw
Potato, boiled
```

This table helps the website avoid showing the same food many times when several sources contain similar entries.

### food_matches

Connects one canonical food to one or more source foods.

Example:

```text
canonical food: Banana, raw
source food: NEVO banana
source food: ANSES banana
source food: BLS banana
```

This allows the website to show one clean food to the user while still keeping the original source values behind it.

## Why Not One Large Table

Putting all sources into one huge table would be simpler at first, but it would become hard to maintain.

Different sources have:

- different nutrient codes;
- different nutrient counts;
- different units;
- different category structures;
- different references;
- different missing value rules;
- different licenses and attribution requirements.

A normalized model is better for long-term learning and future growth.

## Deduplication Strategy

The project should avoid showing duplicate foods to users, but it should not destroy the original source data.

The recommended approach is:

1. Import source data exactly enough to preserve traceability.
2. Normalize nutrient names and units.
3. Create canonical foods for clean user-facing names.
4. Match source foods to canonical foods.
5. Keep match information, including confidence and method.

Possible match methods:

```text
manual
exact_name
normalized_name
fuzzy_match
reviewed_fuzzy_match
```

This is an important data engineering concept called entity resolution.

## Open Food Facts Direction

Open Food Facts should be treated slightly differently from NEVO, ANSES, and BLS.

NEVO, ANSES, and BLS are food composition databases. Open Food Facts is mainly a branded product database.

For Open Food Facts, the project should preserve raw JSON or JSONL records when possible. This is useful for learning JSON processing and for keeping all original product metadata.

A future Open Food Facts model could include:

```text
openfood_products
openfood_product_nutrients
```

The raw JSON can be stored for audit and later parsing.

## Data Quality Principles

The project should make data limitations visible instead of hiding them.

Important rules:

- unknown values are not the same as zero;
- missing values should be tracked;
- source and license should be visible;
- nutrient units must be clear;
- `per_100g` data should not be mixed blindly with per-serving data;
- calculations should explain when results may be incomplete.

The current calculator dataset is based on an Appendix H food composition table, not on a direct modern USDA FoodData Central export. The appendix states that its nutrient database was compiled from several sources, including a USDA Standard Release database and manufacturers' data. This matters because some manufacturer-supplied rows may have incomplete micronutrient or fatty acid values.

## Attribution And Disclaimer

The website should include a public page for:

- data sources;
- source links;
- licenses or usage conditions;
- required attribution text;
- limitations of the calculations;
- missing value explanation;
- medical disclaimer.

The tool should be presented as educational and informational, not as medical advice.

## Learning Goals

This project should help develop practical skills in:

- reading unfamiliar datasets;
- profiling data;
- designing relational schemas;
- normalizing source data;
- mapping nutrient codes;
- handling missing values;
- importing CSV, Excel, and JSON data;
- building repeatable import scripts;
- writing SQL queries;
- building APIs with FastAPI;
- building a frontend with Next.js;
- documenting technical decisions;
- using Git and GitHub professionally.

## Suggested Next Steps

1. Add `temp/` to `.gitignore` so large local data files are not committed by accident.
2. Profile the NEVO dataset first because it has clean CSV files and a clear nutrient dictionary.
3. Write notes about the NEVO file structure.
4. Design the first version of the external source schema.
5. Create a migration for the new source tables.
6. Build a dry-run importer for NEVO.
7. Validate imported row counts, nutrient counts, and missing values.
8. Repeat the process for ANSES and BLS.
9. Add source attribution and disclaimer pages to the website.
10. Later, add Open Food Facts as a JSON/JSONL learning path.
