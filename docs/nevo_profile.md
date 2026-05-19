# NEVO Dataset Profile

This document summarizes the initial profiling work for the NEVO 2025 dataset.

The goal of this profiling step is to understand the dataset before designing database tables or writing an importer. This follows a data engineering workflow: inspect first, model second, import third.

## Source Files

Local files inspected:

```text
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Nutrienten_Nutrients.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Details.csv
```

Related files available for later analysis:

```text
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Recepten_Recipes.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Referenties_References.csv
temp/EuropeNutrientsDBs/nevo/Conditions of use NEVO-online 2025 dataset.pdf
temp/EuropeNutrientsDBs/nevo/NEVO-online background information 2025.pdf
```

Profiling script:

```text
backend/scripts/external_sources/profile_nevo.py
```

## Main File Structure

Main file:

```text
NEVO2025_v9.0.csv
```

Observed profile:

```text
Rows: 2328
Columns: 148
Metadata columns: 11
Nutrient columns: 137
```

The file is in wide format:

```text
one row = one food
many nutrient columns = nutrient values for that food
```

The first 11 columns describe the food:

```text
NEVO-versie/NEVO-version
Voedingsmiddelgroep
Food group
NEVO-code
Voedingsmiddelnaam/Dutch food name
Engelse naam/Food name
Synoniem
Hoeveelheid/Quantity
Opmerking
Bevat sporen van/Contains traces of
Is verrijkt met/Is fortified with
```

The nutrient columns begin at:

```text
ENERCJ (kJ)
```

## Food Identity

The main source identifier is:

```text
NEVO-code
```

Observed profile:

```text
Unique NEVO codes: 2328
Duplicate NEVO codes: 0
```

Conclusion:

```text
NEVO-code can be used as source_food_code for NEVO source foods.
```

Example rows:

```text
1 | Potatoes and tubers | Potatoes raw | per 100g
2 | Potatoes and tubers | Potatoes new raw | per 100g
3 | Potatoes and tubers | Potatoes old raw | per 100g
4 | Cereal products and types of flour | Pasta white raw | per 100g
5 | Cereal products and types of flour | Rice white raw | per 100g
```

## Categories

NEVO provides an English category column:

```text
Food group
```

Observed profile:

```text
Categories: 27
```

First categories observed:

```text
Alcoholic beverages
Bread
Cereal products and types of flour
Cheese
Cold meat cuts
Eggs
Fats and oils
Fish, crustacean and shellfish
Foods for special nutritional use
Fruits
Herbs and spices
Legumes
Meat and poultry
Meat substitutes and dairy substitutes
Milk and milk products
Miscellaneous foods
Mixed dishes
Non-alcoholic beverages
Nuts and seeds
Pastry and biscuits
```

## Quantity / Basis

NEVO values are not only per 100 g. There are two observed bases:

```text
per 100g
per 100ml
```

Counts:

```text
per 100g: 2275
per 100ml: 53
```

Conclusion:

The import model should preserve the original basis. It should not assume that all rows are per 100 g.

Suggested future field:

```text
basis
```

Example values:

```text
per_100g
per_100ml
```

## Main Nutrient Completeness

Main nutrients checked:

```text
ENERCC (kcal)
PROT (g)
CHO (g)
FAT (g)
FIBT (g)
```

Observed completeness:

```text
ENERCC (kcal): present=2328, missing=0
PROT (g): present=2328, missing=0
CHO (g): present=2328, missing=0
FAT (g): present=2328, missing=0
FIBT (g): present=2321, missing=7
```

Conclusion:

NEVO has complete values for kcal, protein, carbohydrates, and fat in the main file. Fibre is missing for 7 foods.

## Foods Missing Fibre

Foods missing `FIBT (g)`:

```text
3129 | Foods for special nutritional use | Toddler formula Nestle groeimelk 1+ p 100 ml | per 100ml
3130 | Foods for special nutritional use | Toddler formula Nestle groeimelk 2+ p 100 ml | per 100ml
5215 | Foods for special nutritional use | Toddler formula Albert Heijn Biologisch Standaard 2 p 100 ml | per 100ml
5445 | Foods for special nutritional use | Infant formula Nestle Little steps 1 p 100ml | per 100ml
5446 | Foods for special nutritional use | Toddler formula Nestle Little steps 2 p 100ml | per 100ml
5447 | Foods for special nutritional use | Toddler formula Nestle Little steps 3 p 100ml | per 100ml
5558 | Sugar, sweets and sweet sauces | Dextrose tablets non-fortified | per 100g
```

Observation:

The missing fibre values are concentrated in infant/toddler formulas and one dextrose product. They do not appear to be randomly distributed across the dataset.

Data quality rule:

```text
missing value != zero
```

For import, missing fibre should be stored as `NULL`, not `0`.

## All Nutrient Missing Values

All 137 nutrient columns were checked for missing values.

Top 20 nutrients with the most missing values:

```text
OA (g): present=475, missing=1853
VITK2 (µg): present=503, missing=1825
NT (g): present=569, missing=1759
ZEA (µg): present=1008, missing=1320
ASH (g): present=1032, missing=1296
LYCPN (µg): present=1070, missing=1258
F18:3TTTN3 (g): present=1117, missing=1211
LUTN (µg): present=1120, missing=1208
TRP (mg): present=1137, missing=1191
CRYPXB (µg): present=1206, missing=1122
VITK1 (µg): present=1267, missing=1061
CARTA (µg): present=1279, missing=1049
VITK (µg): present=1298, missing=1030
F21:5CN3 (g): present=1322, missing=1006
TOCPHD (mg): present=1471, missing=857
TOCPHB (mg): present=1472, missing=856
TOCPHG (mg): present=1476, missing=852
TOCPHA (mg): present=1513, missing=815
F10:1TRS (g): present=1529, missing=799
F12:1TRS (g): present=1529, missing=799
```

Observation:

The nutrients with the most missing values are mostly specialized nutrients, such as organic acids, vitamin K subtypes, carotenoids, amino acids, tocopherol forms, and specific fatty acids.

Conclusion:

NEVO is strong for core nutrients, but not every specialized nutrient is available for every food. Missing nutrient values should remain `NULL` during import. They should not be converted to zero unless the source explicitly reports zero.

## Most Complete Nutrients

The same 137 nutrient columns were also sorted by the fewest missing values.

Top 20 most complete nutrients:

```text
ENERCJ (kJ): present=2328, missing=0
ENERCC (kcal): present=2328, missing=0
WATER (g): present=2328, missing=0
PROT (g): present=2328, missing=0
FAT (g): present=2328, missing=0
FACID (g): present=2328, missing=0
FASAT (g): present=2328, missing=0
CHO (g): present=2328, missing=0
PROTPL (g): present=2327, missing=1
PROTAN (g): present=2327, missing=1
SUGAR (g): present=2327, missing=1
STARCH (g): present=2327, missing=1
ALC (g): present=2327, missing=1
NA (mg): present=2326, missing=2
FIBT (g): present=2321, missing=7
FAMSCIS (g): present=2320, missing=8
FAPU (g): present=2319, missing=9
FE (mg): present=2318, missing=10
HAEM (mg): present=2317, missing=11
NHAEM (mg): present=2317, missing=11
```

Observation:

NEVO has complete or near-complete coverage for core nutrition values, including energy, water, protein, fat, fatty acids, saturated fat, carbohydrate, sugar, starch, sodium, fibre, and iron.

Conclusion:

These highly complete nutrients are good candidates for calculator features, frontend summary views, and early import validation checks.

## Nutrient Dictionary

Dictionary file:

```text
NEVO2025_v9.0_Nutrienten_Nutrients.csv
```

Observed profile:

```text
Rows: 142
Unique nutrient codes: 137
Duplicate nutrient code names: 5
```

First nutrient definitions:

```text
ENERCJ | Energy kJ | kJ
ENERCC | Energy kcal | kcal
WATER | Water total | g
PROT | Protein total | g
FAT | Fat total | g
CHO | Carbohydrate available | g
FIBT | Fibre dietary total | g
ALC | Alcohol total | g
OA | Organic acids total | g
ASH | Ash | g
```

## Nutrient Code Comparison

The main file nutrient columns were compared with the nutrient dictionary.

Observed result:

```text
Codes in main file: 137
Codes in dictionary: 137
Main codes missing from dictionary: 0
Dictionary codes not in main file: 0
```

Conclusion:

The main file and the nutrient dictionary are aligned at the unique-code level. Every nutrient column in the main file has a definition in the dictionary, and every unique dictionary code appears in the main file.

This is good for import because nutrient definitions can be loaded from the dictionary and nutrient values can be mapped safely by code.

Important detail:

The dictionary has 142 rows but 137 unique nutrient codes. Five nutrient codes appear twice because they are listed in more than one nutrient group:

```text
PROT
FAT
CHO
FIBT
ASH
```

For import, nutrient identity should be based on the unique `Nutrient-code`, while repeated dictionary rows can be treated as alternate grouping metadata.

## Details File Structure

Details file:

```text
NEVO2025_v9.0_Details.csv
```

Observed profile:

```text
Rows: 270810
Columns: 17
```

The details file is in long format:

```text
one row = one food + one nutrient + one value
```

Important columns:

```text
NEVO-code
Engelse naam/Food name
Hoeveelheid/Quantity
Component group
Nutrient-code
Component
Gehalte/Value
Eenheid/Unit
Broncode/Source code
Referentie/Reference
```

This file is useful because it carries source/reference metadata for nutrient values, while the main file is easier to scan because it has one row per food.

## Details File Relationships

The details file was compared with the main food file and the nutrient dictionary.

Food code comparison:

```text
Food codes in Details: 2328
Food codes in Main: 2328
Details food codes missing from Main: 0
```

Nutrient code comparison:

```text
Nutrient codes in Details: 137
Nutrient codes in dictionary: 137
Details nutrient codes missing from dictionary: 0
```

Conclusion:

The details file is aligned with both the main food file and the nutrient dictionary. Every food code in `Details` exists in the main file, and every nutrient code in `Details` exists in the nutrient dictionary.

## Details Duplicate Behavior

The details file contains repeated `NEVO-code + Nutrient-code` pairs:

```text
Duplicate food/nutrient pairs: 10410
```

This is not automatically a data quality error. Some nutrients appear in more than one component group. For example, protein can appear under both:

```text
Energy and macronutrients
Protein
```

The important quality check is whether the same `NEVO-code + Nutrient-code` pair has conflicting values or units.

Observed result:

```text
Food/nutrient pairs with different value or unit: 0
```

Conclusion:

The repeated pairs do not create conflicting nutrient values. For import, the pipeline can safely deduplicate details rows by food code, nutrient code, value, and unit, or select one value per food code and nutrient code while preserving source/reference metadata separately.

## Main vs Details Value Comparison

The main file and details file were compared for the main calculator-style nutrients:

```text
ENERCC
PROT
CHO
FAT
FIBT
```

The comparison matched values from:

```text
Main file:    nutrient columns such as ENERCC (kcal), PROT (g), FIBT (g)
Details file: NEVO-code + Nutrient-code + Gehalte/Value
```

Observed result:

```text
Main/details mismatches: 0
```

Important detail:

The 7 missing fibre values are missing consistently in both files. In the main file, `FIBT (g)` is blank for those foods. In the details file, there is no `FIBT` row for those same foods. This is treated as aligned missing data, not as a mismatch.

Conclusion:

For the main nutrients checked, the wide-format main file and the long-format details file agree. This supports using the main file for food metadata and the details file for nutrient values during a future NEVO import.

## Details Source and Reference Coverage

The source and reference fields in the details file were profiled.

Observed result:

```text
Unique source codes: 2133
Unique references: 2189
Rows missing source code: 0
Rows missing reference: 0
```

Top source codes:

```text
REF.0472: 14932
MI0201.00270: 8361
MIR002: 7043
REF.0814: 6797
REF.0228: 4569
MI0201.05041: 4230
REF.0431: 3810
REF.0215: 3737
MI0201.02751: 3285
REF.0791: 3031
```

Top references:

```text
logische redenering: Totaal vet = 0 of bijna 0, dit vetzuur is ingeschat als 0: 14932
Vetzuursamenstelling berekend obv het vetzuurpatroon van vergelijkbaar product: 270 Melk rauwe: 8361
Berekend als (gewogen) gemiddelde van meerdere analyses en/of fabrikantgegevens: 7042
NEVO-team Vaststellen logische nullen tbv NEVO (intern document) / Determination of logical value for NEVO (internal document), 2017 RIVM: 6797
Haan HPM de Actualisering van de samenstelling van vlees in de NEVO-tabel, TNO / RIVM 2010, TNO: 4569
```

Observation:

Every details row has source and reference metadata. This is strong from a data lineage perspective because nutrient values can be traced back to a source code and a reference text.

Conclusion:

The future import model should avoid repeating reference text directly on every nutrient-value row. A better model is to store references once and link nutrient values to them.

Possible future mapping:

```text
Broncode/Source code -> source_references.source_code
Referentie/Reference -> source_references.reference_text
source_food_nutrient_values.reference_id -> source_references.id
```

## Import Implications

Recommended future mapping:

```text
NEVO-code -> source_foods.source_food_code
Food group -> source_foods.category_1
Voedingsmiddelnaam/Dutch food name -> source_foods.food_name_original
Engelse naam/Food name -> source_foods.food_name_en
Hoeveelheid/Quantity -> source_foods.basis
Nutrient-code -> nutrients.source_code or nutrient mapping table
Component -> nutrients.source_name
Eenheid/Unit -> nutrients.unit
nutrient value columns -> source_food_nutrient_values.value
Gehalte/Value -> source_food_nutrient_values.value
Broncode/Source code -> source/reference metadata
Referentie/Reference -> source/reference metadata
```

NEVO should be imported into external-source tables, not directly into the current `foods` table.

The current calculator should continue using the current local Appendix H dataset until external-source data is fully modeled, validated, and reviewed.

## Next Profiling Steps

Recommended next checks:

1. Decide how to store `per 100g` and `per 100ml` rows in the database.
2. Draft the external-source database schema before importing NEVO.
