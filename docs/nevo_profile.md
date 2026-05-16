# NEVO Dataset Profile

This document summarizes the initial profiling work for the NEVO 2025 dataset.

The goal of this profiling step is to understand the dataset before designing database tables or writing an importer. This follows a data engineering workflow: inspect first, model second, import third.

## Source Files

Local files inspected:

```text
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0.csv
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Nutrienten_Nutrients.csv
```

Related files available for later analysis:

```text
temp/EuropeNutrientsDBs/nevo/NEVO2025_v9.0_Details.csv
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

## Nutrient Dictionary

Dictionary file:

```text
NEVO2025_v9.0_Nutrienten_Nutrients.csv
```

Observed profile:

```text
Rows: 137
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

The main file and the nutrient dictionary are aligned. Every nutrient column in the main file has a definition in the dictionary, and every dictionary code appears in the main file.

This is good for import because nutrient definitions can be loaded from the dictionary and nutrient values can be mapped safely by code.

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
```

NEVO should be imported into external-source tables, not directly into the current `foods` table.

The current calculator should continue using the current local Appendix H dataset until external-source data is fully modeled, validated, and reviewed.

## Next Profiling Steps

Recommended next checks:

1. Profile `NEVO2025_v9.0_Details.csv`.
2. Compare main file values with details file values for selected nutrients.
3. Check whether all details nutrients are represented in the dictionary.
4. Count missing values across all nutrient columns, not just main macros.
5. Identify nutrients with the most missing values.
6. Review reference/source fields in the details file.
7. Decide how to store `per 100g` and `per 100ml` rows in the database.

