# Data Sources

This project is designed to use public food composition and food product datasets in a transparent way.

The raw datasets are kept locally in `temp/` while they are being studied and processed. They are not committed to Git because they can be large, versioned externally, and subject to specific attribution or redistribution rules.

This document records:

- where each source comes from;
- which local files were downloaded;
- what the source is useful for;
- what attribution or license notes must be respected;
- how the source may fit into the future data model.

Access date for the source checks below: 2026-05-14.

## Current Project Dataset

### Local Appendix H Food Composition Table

Local files:

```text
backend/data/FoodsFinal.xlsx
backend/data/FoodsFinal_with_ro.xlsx
backend/data/FoodsFinal_sample.xlsx
temp/EuropeNutrientsDBs/USDA.pdf
```

Current use:

- powers the existing `/foods` page;
- powers the existing `/calculator` page;
- uses the current app tables:

```text
categories
subcategories
foods
```

Important note:

The current calculator should continue using this dataset for now. External sources should be studied and imported separately before being connected to the calculator.

### Source Notes

The local food table currently used by the app comes from:

```text
Appendix H - Table of Food Composition
```

The PDF explains that the appendix table is updated to reflect current nutrient data, remove outdated foods, and add foods that are new to the marketplace.

The appendix also explains that the nutrient database was compiled from a variety of sources, including:

```text
USDA Standard Release database
manufacturers' data
```

This means the current dataset should be described as USDA-and-manufacturer-based, not as a direct USDA FoodData Central export.

### Format Notes

The current source table is organized differently from NEVO, ANSES, and BLS.

It uses serving-based rows:

```text
DA+ code
Food Description
Quantity
Measure
Wt (g)
nutrient values for that quantity / measure
```

The calculator scales values by:

```text
user grams / Wt (g)
```

This is different from NEVO, ANSES, and BLS, which are mostly expressed per 100 g.

### Missing Value Notes

The Appendix H documentation makes an important distinction:

```text
dash = unknown or unavailable
0 = nutrient is considered absent
```

For calculations, the app may use zero when a value is missing, but the result should be marked as incomplete when source data are unknown.

The appendix also notes that manufacturer data can be incomplete because manufacturers usually provide only the nutrients required on food labels.

### Attribution Draft

Until the exact textbook / publisher citation is finalized, use cautious wording:

```text
Current calculator data are based on an Appendix H food composition table compiled from
USDA Standard Release data and manufacturers' data. Values are estimates and may be incomplete.
```

Before public launch, this section should be replaced with the exact bibliographic citation for the PDF/source document.

## NEVO

### Source

Name:

```text
NEVO online version 2025/9.0
```

Publisher:

```text
RIVM - National Institute for Public Health and the Environment, Netherlands
```

Official pages:

- https://www.rivm.nl/en/dutch-food-composition-database/use-of-nevo-online/request-dataset
- https://www.rivm.nl/en/dutch-food-composition-database/access-nevo-data
- https://www.rivm.nl/documenten/conditions-for-use-of-nevo-online-version

### Local Files

```text
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Details.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Nutrienten_Nutrients.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Recepten_Recipes.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Referenties_References.csv
temp/EuropeNutrientsDBs/nevo/Conditions of use NEVO-online 2025 dataset.pdf
temp/EuropeNutrientsDBs/nevo/NEVO-online background information 2025.pdf
```

### What It Contains

NEVO 2025/9.0 contains food composition data for 2,328 foods and approximately 130 nutrients.

The data are mainly expressed per 100 g edible portion. Some liquid foods may be expressed per 100 ml when this is indicated in the food name or documentation.

Useful fields:

```text
NEVO-code
Food group
Dutch food name
English food name
Quantity
Nutrient-code
Value
Unit
Source code
Reference
```

### Format Notes

The main file is wide format:

```text
one food row, many nutrient columns
```

The details file is long format:

```text
one food + one nutrient per row
```

This makes NEVO a good first source for learning data profiling, normalization, and nutrient mapping.

### Attribution And Use Notes

RIVM states that the nutritional value and corresponding source information for NEVO online 2025/9.0 can be downloaded for free after agreeing to the conditions of use.

The conditions require source and version attribution. The reference text to use is:

```text
NEVO online version 2025/9.0, RIVM, Bilthoven.
```

For output from calculation software, the conditions mention attribution such as:

```text
Based on data from NEVO online version 2025/9.0, RIVM, Bilthoven.
```

If NEVO is combined with other data sources, the attribution should make that clear.

Important caution:

- keep the original NEVO values traceable;
- do not silently modify original values;
- if additional values are added, mark them clearly as additions and not original NEVO data.

### Planned Use In This Project

Recommended first external import source.

Why:

- CSV files are easier to inspect;
- nutrient dictionary is available;
- references are available;
- the structure is clear for learning data engineering basics.

## ANSES / Ciqual

### Source

Name:

```text
Ciqual French food composition table 2025
```

Publisher:

```text
ANSES / Ciqual, France
```

Official pages:

- https://ciqual.anses.fr/cms/en/2025-anses-ciqual-table
- https://www.anses.fr/en/content/ciqual-nutritional-composition-table
- https://zenodo.org/records/17550133

DOI:

```text
10.5281/zenodo.17550133
```

### Local Files

```text
temp/EuropeNutrientsDBs/anses/Table Ciqual 2025_ENG_2025_11_03.xlsx
temp/EuropeNutrientsDBs/anses/Table Ciqual 2025 doc ENG_2025_11_19.pdf
```

### What It Contains

The 2025 ANSES-CIQUAL table includes:

```text
3,484 foods
74 components
```

Useful fields:

```text
alim_grp_code
alim_ssgrp_code
alim_ssssgrp_code
alim_grp_nom_eng
alim_ssgrp_nom_eng
alim_ssssgrp_nom_eng
alim_code
alim_nom_eng
Energy kcal / 100g
Water / 100g
Protein / 100g
Carbohydrate / 100g
Fat / 100g
Fibres / 100g
vitamins and minerals
```

### Format Notes

The Excel file is mostly wide format:

```text
one food row, many nutrient columns
```

The dataset has a clear category hierarchy with multiple food group levels.

### Attribution And License Notes

The Zenodo record states that the data are public and must not be reproduced without clear source indication.

Recommended citation:

```text
Anses. 2025. Ciqual French food composition table.
```

For scientific or detailed citation:

```text
Anses. 2025. Ciqual French food composition table 2025. doi:10.5281/zenodo.17550133
```

The Zenodo record lists rights including:

```text
Creative Commons Attribution 4.0 International
Etalab Open License 2.0
```

### Planned Use In This Project

Recommended second external source after NEVO.

Why:

- clean Excel structure;
- clear English labels;
- good source citation;
- useful French food composition reference.

## BLS

### Source

Name:

```text
Bundeslebensmittelschluessel (BLS), Version 4.0 - German Nutrient Database
```

Publisher:

```text
Max Rubner-Institut (MRI), Germany
```

Official pages:

- https://blsdb.de/download
- https://www.mri.bund.de/en/institutes/nutritional-behaviour/translate-to-english-arbeitsbereiche/german-nutrient-database-bundeslebensmittelschluessel-bl/

DOI:

```text
10.25826/Data20251217-134202-0
```

### Local Files

```text
temp/EuropeNutrientsDBs/bls/BLS_4_0_2025_DE.zip
temp/EuropeNutrientsDBs/bls/BLS_4_0_2025_DE/BLS_4_0_Daten_2025_DE.xlsx
temp/EuropeNutrientsDBs/bls/BLS_4_0_2025_DE/BLS_4_0_Components_DE_EN.xlsx
temp/EuropeNutrientsDBs/bls/BLS_4_0_2025_DE/BLS_4_0_Dokumentation_DE.pdf
```

### What It Contains

BLS 4.0 contains approximately:

```text
7,140 foods
138 nutrients
```

Useful fields:

```text
BLS Code
German food name
English food name
nutrient value columns
data origin columns
reference columns
```

### Format Notes

BLS is richer and more complex than NEVO and ANSES.

For many nutrients, the data file contains:

```text
value
data origin
reference
```

This makes BLS very useful for traceability, but it also makes the import more complex.

### Attribution And License Notes

The BLS download page states that the data are available as Open Data under:

```text
CC BY 4.0
```

The Max Rubner-Institut must be named as publisher.

Citation:

```text
Max Rubner-Institut (2025): Bundeslebensmittelschluessel (BLS), Version 4.0 - Deutsche Naehrstoffdatenbank. Karlsruhe. DOI: 10.25826/Data20251217-134202-0
```

### Planned Use In This Project

Recommended third external import source.

Why:

- very rich nutrient coverage;
- source/reference metadata for nutrient values;
- more complex structure, so it is better after practicing with NEVO and ANSES.

## Open Food Facts

### Source

Name:

```text
Open Food Facts
```

Official pages:

- https://world.openfoodfacts.org/
- https://world.openfoodfacts.org/data
- https://openfoodfacts.github.io/openfoodfacts-server/api/tutorials/license-be-on-the-legal-side/
- https://support.openfoodfacts.org/help/en-gb/12-api-data-reuse/88-how-can-i-access-collect-data-for-my-projects

### What It Contains

Open Food Facts is different from NEVO, ANSES, and BLS.

It is mainly a collaborative branded product database with:

```text
barcodes
product names
brands
ingredients
allergens
labels
categories
nutrition facts
images
countries
packaging and metadata
```

### Format Notes

Open Food Facts is useful for learning JSON and JSONL because product records can contain nested fields, such as:

```text
nutriments
categories_tags
ingredients
images
ecoscore_data
```

For this project:

- CSV is easier for quick table-style exploration;
- JSONL is better for learning nested data processing and preserving raw product records.

Recommended learning path:

1. Start with a small JSONL sample.
2. Preserve raw JSON.
3. Extract selected fields into relational tables.
4. Later evaluate CSV or Parquet for larger analysis.

### Attribution And License Notes

Open Food Facts documentation states:

```text
database: Open Database License (ODbL)
database contents: Database Contents License
product images: Creative Commons Attribution ShareAlike
```

Important:

- attribution is required;
- reuse must follow the Open Food Facts terms;
- derived or mixed databases may have share-alike obligations under ODbL;
- image licensing is separate from database licensing.

### Planned Use In This Project

Open Food Facts should be treated as branded product data, not as the same type of generic food composition data as NEVO, ANSES, or BLS.

Recommended future tables:

```text
openfood_products
openfood_product_nutrients
```

Recommended fields to preserve:

```text
barcode
product_name
brands
countries
categories_tags
nutriments
raw_json
```

## Future Data Model Direction

The recommended long-term model is:

```text
data_sources
source_foods
nutrients
source_food_nutrient_values
canonical_foods
food_matches
```

This lets the project:

- add new sources later;
- avoid mixing unrelated source formats;
- preserve source lineage;
- compare nutrient values between sources;
- deduplicate foods for the user interface;
- keep the current calculator stable while external sources are still being studied.

## Public Site Attribution Draft

The public website should include a Data Sources page with language similar to:

```text
This website uses nutrition data from public food composition databases and product datasets.
Current and future sources may include NEVO online version 2025/9.0 (RIVM, Bilthoven),
the ANSES-CIQUAL French food composition table 2025, the Bundeslebensmittelschluessel
(BLS) Version 4.0 from the Max Rubner-Institut, and Open Food Facts.

Nutrition calculations are estimates based on available data. Missing values do not mean zero.
The tool is for informational and educational use and does not replace professional medical,
nutrition, or dietetic advice.
```

Each source should also have its own exact attribution text and link.

## Next Steps

1. Keep `temp/` ignored by Git.
2. Profile NEVO first.
3. Create a small data profiling script for NEVO.
4. Design the external source database schema.
5. Create migrations for the new tables.
6. Build a dry-run NEVO importer.
7. Validate counts, missing values, and nutrient mappings.
8. Repeat the profiling/import process for ANSES and BLS.
9. Add Open Food Facts later as a JSON/JSONL learning path.
