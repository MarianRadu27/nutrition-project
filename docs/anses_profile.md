# ANSES/Ciqual Dataset Profile

This document summarizes the initial profiling work for the ANSES/Ciqual 2025 dataset.

The goal of this profiling step is to understand the dataset before designing database tables or writing an importer. This follows the same workflow used for NEVO: inspect first, model second, import third.

## Source Files

Local files inspected:

```text
temp/EuropeNutrientsDBs/anses/Table Ciqual 2025_ENG_2025_11_03.xlsx
temp/EuropeNutrientsDBs/anses/Table Ciqual 2025 doc ENG_2025_11_19.pdf
```

Profiling script:

```text
backend/scripts/external_sources/profile_anses.py
```

## Workbook Structure

Main workbook:

```text
Table Ciqual 2025_ENG_2025_11_03.xlsx
```

Observed sheet names:

```text
food composition
INFOODS codes
```

The current profiling focuses on:

```text
food composition
```

## Food Composition Sheet

Observed profile:

```text
Rows: 3485
Columns: 84
Metadata columns: 9
Nutrient columns: 75
```

The file is in wide format:

```text
one row = one food
many nutrient columns = nutrient values for that food
```

The first 9 columns describe the food:

```text
alim_grp_code
alim_ssgrp_code
alim_ssssgrp_code
alim_grp_nom_eng
alim_ssgrp_nom_eng
alim_ssssgrp_nom_eng
alim_code
alim_nom_eng
alim_nom_sci
```

The nutrient columns begin at:

```text
Energy,
Regulation
EU No
1169
2011 (kJ
100g)
```

Observation:

The nutrient headers contain line breaks. The importer should not rely on manually typed column names more than necessary. Important column names should be stored as constants or mapped through a controlled dictionary.

## Food Identity

The main source identifier appears to be:

```text
alim_code
```

Observed profile:

```text
Unique food codes: 3484
Duplicate food codes: 0
```

Conclusion:

`alim_code` can be used as `source_food_code` for ANSES/Ciqual source foods.

Example rows:

```text
24999 | - | - | - | Dessert (average)
8406 | starters and dishes | mixed salads | - | Salad of pig's snout, with sauce, prepacked
8407 | starters and dishes | mixed salads | - | Salad of saveloy, with sauce, prepacked
25600 | starters and dishes | mixed salads | - | Celeriac salad, with remoulade sauce, prepacked
25601 | starters and dishes | mixed salads | - | Tuna salad, with vegetables, canned
```

## Categories

ANSES/Ciqual provides three English category levels:

```text
alim_grp_nom_eng
alim_ssgrp_nom_eng
alim_ssssgrp_nom_eng
```

Observed profile:

```text
Categories: 11
Subcategories: 64
Subsubcategories: 77
```

Placeholder counts:

```text
Category placeholder rows: 1
Subcategory placeholder rows: 2
Subsubcategory placeholder rows: 1450
```

The placeholder value is:

```text
-
```

Important distinction:

The placeholder should be checked with exact equality:

```text
value == "-"
```

It should not be checked with substring logic such as:

```text
"-" in value
```

Reason:

Some valid category names contain hyphens, such as `non-alcoholic beverages`. These are real category values and should not be treated as missing.

First observed categories:

```text
baby food
beverages
cereal products
fats and oils
fruits, vegetables, legumes and nuts
ice cream and sorbet
meat, egg and fish
milk and milk products
miscellaneous
starters and dishes
sugar and confectionery
```

First observed subcategories:

```text
Viennese pastries
alcoholic beverages
baby biscuits and cereals
baby deserts
baby dishes
baby milk and beverages
breads and similar
breakfast cereals
butters
cakes and pastry
cereal bars
cheese and similar
chocolate and chocolate products
condiments
cooked meat
cooking aids
cream and similar
dairy products
delicatessen meat and similar
dishes
```

First observed subsubcategories:

```text
beef and veal
beers and ciders
beverages, to reconstitute
blue cheeses
breads
canned fruits
cheese dishes
cocktails
coffee, tea, cocoa beverages, etc. ready to drink
cold sauces
cooked ham
dairy beverages
dairy desserts
dessert sauces
dried fruits
dried herbs
dry sausages
eggs, cooked
eggs, raw
fish dishes, no garnish
```

Conclusion:

The ANSES/Ciqual category model is more structured than the current local food table. It has three category levels, but the third level is not always present. Placeholder category values should be stored as `NULL` during import.

## Import Implications

Recommended future mapping:

```text
alim_code -> source_foods.source_food_code
alim_nom_eng -> source_foods.food_name_en
alim_nom_sci -> source_foods.scientific_name or notes
alim_grp_nom_eng -> source_foods.category_1
alim_ssgrp_nom_eng -> source_foods.category_2
alim_ssssgrp_nom_eng -> source_foods.category_3
nutrient columns -> source_food_nutrient_values.value
```

ANSES/Ciqual should be imported into external-source tables, not directly into the current `foods` table.

The current calculator should continue using the existing local Appendix H dataset until external-source data is fully modeled, validated, and reviewed.

## Next Profiling Steps

Recommended next checks:

1. Profile missing values across the 75 nutrient columns.
2. Identify nutrients that are complete or nearly complete.
3. Inspect the `INFOODS codes` sheet.
4. Check whether nutrient units can be parsed consistently from headers.
5. Compare ANSES/Ciqual nutrient structure with the NEVO nutrient model.
