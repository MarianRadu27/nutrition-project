"use client";

import { useEffect, useMemo, useState } from "react";


type Lang = "en" | "ro";

type Category = {
  id: number;
  name: string;
  name_ro: string | null;
  name_display: string;
};

type Subcategory = {
  id: number;
  category_id: number;
  name: string;
  name_ro: string | null;
  name_display: string;
};

type Food = {
  id: number;
  da_code: number;
  subcategory_id: number | null;
  category_id: number | null;
  name_display: string;
  category_name_display: string | null;
  subcategory_name_display: string | null;
  quantity: number | null;
  measure: string | null;
  wt_g: number | null;
  ener_kcal: number | null;
  prot_g: number | null;
  carbo_g: number | null;
  fat_g: number | null;
  fiber_g: number | null;
};

type FoodsResponse = {
  items: Food[];
  limit: number;
  offset: number;
  count: number;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
const LANG_KEY = "app_lang";

function formatNumber(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "-";
  }
  return value.toFixed(2);
}

export default function FoodsPage() {
  const [lang, setLang] = useState<Lang>("en");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>("");
  const [selectedSubcategoryId, setSelectedSubcategoryId] = useState<string>("");
  const [foodsData, setFoodsData] = useState<FoodsResponse | null>(null);
  const [loading, setLoading] = useState(false);
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

  useEffect(() => {
    async function loadCategories() {
      const response = await fetch(`${API_BASE}/api/categories?lang=${lang}`);
      if (!response.ok) {
        throw new Error("Failed to load categories");
      }
      const data = (await response.json()) as Category[];
      setCategories(data);
    }

    loadCategories().catch((err: unknown) => {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    });
  }, [lang]);

  useEffect(() => {
    if (!selectedCategoryId) {
      setSubcategories([]);
      setSelectedSubcategoryId("");
      return;
    }

    async function loadSubcategories() {
      const response = await fetch(
        `${API_BASE}/api/categories/${selectedCategoryId}/subcategories?lang=${lang}`,
      );
      if (!response.ok) {
        throw new Error("Failed to load subcategories");
      }
      const data = (await response.json()) as Subcategory[];
      setSubcategories(data);
    }

    loadSubcategories().catch((err: unknown) => {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    });
  }, [selectedCategoryId, lang]);

  const foodsUrl = useMemo(() => {
    const params = new URLSearchParams();
    params.set("lang", lang);
    params.set("limit", "100");
    params.set("offset", "0");
    if (search.trim()) {
      params.set("search", search.trim());
    }
    if (selectedCategoryId) {
      params.set("category_id", selectedCategoryId);
    }
    if (selectedSubcategoryId) {
      params.set("subcategory_id", selectedSubcategoryId);
    }
    return `${API_BASE}/api/foods?${params.toString()}`;
  }, [lang, search, selectedCategoryId, selectedSubcategoryId]);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(foodsUrl)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Failed to load foods");
        }
        const data = (await response.json()) as FoodsResponse;
        setFoodsData(data);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Unknown error";
        setError(message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [foodsUrl]);

  return (
    <main style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>Foods</h1>
      <p>Browse foods and base nutrients per serving.</p>

      <section style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
        <button
          type="button"
          onClick={() => setLang("en")}
          disabled={lang === "en"}
          style={{ padding: "6px 12px" }}
        >
          EN
        </button>
        <button
          type="button"
          onClick={() => setLang("ro")}
          disabled={lang === "ro"}
          style={{ padding: "6px 12px" }}
        >
          RO
        </button>
      </section>

      <section style={{ display: "grid", gap: 12, maxWidth: 960, marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search food name..."
            style={{ flex: 1, padding: 8 }}
          />
          <button type="button" onClick={() => setSearch(searchInput)}>
            Search
          </button>
        </div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <select
            value={selectedCategoryId}
            onChange={(event) => {
              setSelectedCategoryId(event.target.value);
              setSelectedSubcategoryId("");
            }}
            style={{ padding: 8, minWidth: 240 }}
          >
            <option value="">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={String(category.id)}>
                {category.name_display}
              </option>
            ))}
          </select>

          <select
            value={selectedSubcategoryId}
            onChange={(event) => setSelectedSubcategoryId(event.target.value)}
            style={{ padding: 8, minWidth: 240 }}
            disabled={!selectedCategoryId}
          >
            <option value="">All subcategories</option>
            {subcategories.map((subcategory) => (
              <option key={subcategory.id} value={String(subcategory.id)}>
                {subcategory.name_display}
              </option>
            ))}
          </select>
        </div>
      </section>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {!loading && foodsData && (
        <section>
          <p>
            Showing {foodsData.items.length} / {foodsData.count}
          </p>
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 980 }}>
              <thead>
                <tr>
                  {[
                    "Food",
                    "Category",
                    "Subcategory",
                    "Qty",
                    "Measure",
                    "Wt (g)",
                    "Kcal",
                    "Protein (g)",
                    "Carbs (g)",
                    "Fat (g)",
                    "Fiber (g)",
                  ].map((header) => (
                    <th
                      key={header}
                      style={{
                        border: "1px solid #ccc",
                        padding: 8,
                        textAlign: "left",
                        backgroundColor: "#f4f4f4",
                      }}
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {foodsData.items.map((food) => (
                  <tr key={food.id}>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>{food.name_display}</td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {food.category_name_display ?? "-"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {food.subcategory_name_display ?? "-"}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {formatNumber(food.quantity)}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>{food.measure ?? "-"}</td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>{formatNumber(food.wt_g)}</td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {formatNumber(food.ener_kcal)}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>{formatNumber(food.prot_g)}</td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {formatNumber(food.carbo_g)}
                    </td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>{formatNumber(food.fat_g)}</td>
                    <td style={{ border: "1px solid #ddd", padding: 8 }}>
                      {formatNumber(food.fiber_g)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
