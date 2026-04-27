import pandas as pd
from pathlib import Path

INPUT_FILE = Path("D:/nutrition-project/foods_translate_work.xlsx")
OUTPUT_FILE = Path("D:/nutrition-project/foods_translate_step1.xlsx")
GLOSSARY_FILE = Path("D:/nutrition-project/backend/scripts/translation/glossary_ro.csv")

SOURCE_COL = "food_description"
TARGET_COL = "food_description_ro"
TRANSLATION_STATUS = "translation_status"

df = pd.read_excel(INPUT_FILE)
glossary_df = pd.read_csv(GLOSSARY_FILE)

print("Coloane disponibile:")
print(df.columns.tolist())

if SOURCE_COL not in df.columns:
    raise ValueError(f"Coloana sursa '{SOURCE_COL}' nu exista in fisier")

glossary = {}
for _, row in glossary_df.iterrows():
    en = str(row["en"]).strip()
    ro = str(row["ro"]).strip()
    glossary[en] = ro


def apply_glossary(text: str) -> str:
    result = text
    for en, ro in glossary.items():
        result = result.replace(en, ro)
    return result


def translate_with_status(value):
    if pd.isna(value):
        return (None, "empty")

    text = str(value).strip()
    if not text:
        return (None, "empty")

    translated = apply_glossary(text)

    if translated == text:
        return (translated, "needs_review")

    return (translated, "auto_glossary")


results = df[SOURCE_COL].apply(translate_with_status)
df[TARGET_COL] = results.apply(lambda x: x[0])
df[TRANSLATION_STATUS] = results.apply(lambda x: x[1])

print(f"Numar randuri: {len(df)}")
print(df[[SOURCE_COL, TARGET_COL, TRANSLATION_STATUS]].head(20))
print(df[TRANSLATION_STATUS].value_counts(dropna=False))

df.to_excel(OUTPUT_FILE, index=False)
print(f"Fisier salvat: {OUTPUT_FILE}")