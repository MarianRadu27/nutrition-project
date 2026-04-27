"use client";

import { useEffect, useMemo, useState } from "react";

type Lang = "en" | "ro";

type FoodSearchItem = {
  id: number;
  name_display: string;
  wt_g: number | null;
};

type MealEntry = {
  food_id: number;
  name: string;
  grams: number;
};

type CalcItem = {
  food_id: number;
  name: string;
  grams: number;
  factor: number | null;
  nutrients: {
    kcal: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
  };
  incomplete_data: boolean;
  error: string | null;
};

type CalcResponse = {
  totals: {
    kcal: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
  };
  incomplete_data: boolean;
  items: CalcItem[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
const LANG_KEY = "app_lang";

function formatNumber(value: number): string {
  return value.toFixed(2);
}

export default function CalculatorPage() {
  const [lang, setLang] = useState<Lang>("en");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<FoodSearchItem[]>([]);
  const [mealItems, setMealItems] = useState<MealEntry[]>([]);
  const [calcResult, setCalcResult] = useState<CalcResponse | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingCalc, setLoadingCalc] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem(LANG_KEY);
    if (stored === "en" || stored === "ro") {
      setLang(stored);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(LANG_KEY, lang);
  }, [lang]);

  const searchUrl = useMemo(() => {
    const params = new URLSearchParams();
    params.set("lang", lang);
    params.set("limit", "20");
    params.set("offset", "0");
    if (searchQuery.trim()) {
      params.set("search", searchQuery.trim());
    }
    return `${API_BASE}/api/foods?${params.toString()}`;
  }, [lang, searchQuery]);

  useEffect(() => {
    setLoadingSearch(true);
    setError(null);
    fetch(searchUrl)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Failed to search foods");
        }
        const payload = (await response.json()) as { items: FoodSearchItem[] };
        setSearchResults(payload.items);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Unknown error";
        setError(message);
      })
      .finally(() => setLoadingSearch(false));
  }, [searchUrl]);

  function addFood(food: FoodSearchItem) {
    setMealItems((current) => {
      const exists = current.some((item) => item.food_id === food.id);
      if (exists) {
        return current;
      }
      return [
        ...current,
        {
          food_id: food.id,
          name: food.name_display,
          grams: 100,
        },
      ];
    });
  }

  function updateGrams(foodId: number, grams: number) {
    setMealItems((current) =>
      current.map((item) => (item.food_id === foodId ? { ...item, grams } : item)),
    );
  }

  function removeMealItem(foodId: number) {
    setMealItems((current) => current.filter((item) => item.food_id !== foodId));
  }

  async function calculateMeal() {
    if (mealItems.length === 0) {
      setError("Add at least one food before calculating");
      return;
    }

    setLoadingCalc(true);
    setError(null);
    setCalcResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/calc/meal?lang=${lang}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: mealItems.map((item) => ({
            food_id: item.food_id,
            grams: item.grams,
          })),
        }),
      });

      if (!response.ok) {
        const payload = (await response.json()) as { detail?: string };
        throw new Error(payload.detail ?? "Calculation failed");
      }

      const payload = (await response.json()) as CalcResponse;
      setCalcResult(payload);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    } finally {
      setLoadingCalc(false);
    }
  }

  return (
    <main style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>Meal Calculator</h1>
      <p>Compute totals by grams using wt_g as scaling base.</p>

      <section style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <button type="button" onClick={() => setLang("en")} disabled={lang === "en"}>
          EN
        </button>
        <button type="button" onClick={() => setLang("ro")} disabled={lang === "ro"}>
          RO
        </button>
      </section>

      <section style={{ display: "grid", gap: 8, marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search foods..."
            style={{ flex: 1, padding: 8 }}
          />
          <button type="button" onClick={() => setSearchQuery(searchInput)}>
            Search
          </button>
        </div>

        {loadingSearch && <p>Searching...</p>}
        {!loadingSearch && (
          <div style={{ display: "grid", gap: 6 }}>
            {searchResults.map((food) => (
              <div
                key={food.id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  border: "1px solid #ddd",
                  padding: 8,
                }}
              >
                <div>
                  <strong>{food.name_display}</strong>
                  <div>wt_g: {food.wt_g ?? "-"}</div>
                </div>
                <button type="button" onClick={() => addFood(food)}>
                  Add
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <section style={{ marginBottom: 16 }}>
        <h2>Meal Items</h2>
        {mealItems.length === 0 && <p>No foods selected yet.</p>}
        <div style={{ display: "grid", gap: 8 }}>
          {mealItems.map((item) => (
            <div
              key={item.food_id}
              style={{ display: "flex", gap: 8, alignItems: "center", border: "1px solid #ddd", padding: 8 }}
            >
              <div style={{ flex: 1 }}>{item.name}</div>
              <label>
                grams:
                <input
                  type="number"
                  value={item.grams}
                  min={0.1}
                  step={0.1}
                  onChange={(event) =>
                    updateGrams(item.food_id, Number(event.target.value))
                  }
                  style={{ marginLeft: 6, width: 100 }}
                />
              </label>
              <button type="button" onClick={() => removeMealItem(item.food_id)}>
                Remove
              </button>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={calculateMeal}
          disabled={loadingCalc || mealItems.length === 0}
          style={{ marginTop: 12 }}
        >
          {loadingCalc ? "Calculating..." : "Calculate"}
        </button>
      </section>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {calcResult && (
        <section>
          <h2>Totals</h2>
          {calcResult.incomplete_data && (
            <p style={{ color: "darkorange" }}>
              Warning: some nutrients are missing, totals may be underestimated.
            </p>
          )}
          <ul>
            <li>Kcal: {formatNumber(calcResult.totals.kcal)}</li>
            <li>Protein (g): {formatNumber(calcResult.totals.protein_g)}</li>
            <li>Carbs (g): {formatNumber(calcResult.totals.carbs_g)}</li>
            <li>Fat (g): {formatNumber(calcResult.totals.fat_g)}</li>
            <li>Fiber (g): {formatNumber(calcResult.totals.fiber_g)}</li>
          </ul>

          <h3>Items</h3>
          <div style={{ display: "grid", gap: 8 }}>
            {calcResult.items.map((item) => (
              <div key={item.food_id} style={{ border: "1px solid #ddd", padding: 8 }}>
                <strong>{item.name}</strong> ({item.grams} g)
                {item.error && <p style={{ color: "crimson" }}>{item.error}</p>}
                {!item.error && (
                  <ul>
                    <li>factor: {item.factor?.toFixed(4)}</li>
                    <li>kcal: {formatNumber(item.nutrients.kcal)}</li>
                    <li>protein_g: {formatNumber(item.nutrients.protein_g)}</li>
                    <li>carbs_g: {formatNumber(item.nutrients.carbs_g)}</li>
                    <li>fat_g: {formatNumber(item.nutrients.fat_g)}</li>
                    <li>fiber_g: {formatNumber(item.nutrients.fiber_g)}</li>
                  </ul>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
