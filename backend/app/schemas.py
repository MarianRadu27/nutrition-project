from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Lang = Literal["en", "ro"]


class CategoryOut(BaseModel):
    id: int
    name: str
    name_ro: str | None = None
    name_display: str


class SubcategoryOut(BaseModel):
    id: int
    category_id: int
    name: str
    name_ro: str | None = None
    name_display: str


class FoodOut(BaseModel):
    id: int
    da_code: int
    subcategory_id: int | None = None
    category_id: int | None = None
    food_description: str
    food_description_ro: str | None = None
    name_display: str
    quantity: float | None = None
    measure: str | None = None
    wt_g: float | None = None
    ener_kcal: float | None = None
    prot_g: float | None = None
    carbo_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    category_name_display: str | None = None
    subcategory_name_display: str | None = None

class FoodDetailOut(BaseModel):
    id: int
    da_code: int
    subcategory_id: int | None = None
    category_id: int | None = None
    food_description: str
    food_description_ro: str | None = None
    name_display: str
    quantity: float | None = None
    measure: str | None = None
    wt_g: float | None = None
    h2o_g: float | None = None
    ener_kcal: float | None = None
    prot_g: float | None = None
    carbo_g: float | None = None
    fiber_g: float | None = None
    fat_g: float | None = None
    sat_g: float | None = None
    mono_g: float | None = None
    poly_g: float | None = None
    trans_g: float | None = None
    chol_mg: float | None = None
    calc_mg: float | None = None
    iron_mg: float | None = None
    magn_mg: float | None = None
    pota_mg: float | None = None
    sodi_mg: float | None = None
    zinc_mg: float | None = None
    vit_a_ug: float | None = None
    vit_e_mg: float | None = None
    thia_mg: float | None = None
    ribo_mg: float | None = None
    niac_mg: float | None = None
    vit_b6_mg: float | None = None
    fola_ug: float | None = None
    vit_c_mg: float | None = None
    vit_b12_ug: float | None = None
    sele_ug: float | None = None
    category_name_display: str | None = None
    subcategory_name_display: str | None = None
    

class FoodsListResponse(BaseModel):
    items: list[FoodOut]
    limit: int
    offset: int
    count: int


class MealCalcItemIn(BaseModel):
    food_id: int = Field(gt=0)
    grams: float = Field(gt=0)


class MealCalcRequest(BaseModel):
    items: list[MealCalcItemIn]

    @model_validator(mode="after")
    def validate_items(self) -> "MealCalcRequest":
        if not self.items:
            raise ValueError("items must contain at least one entry")
        return self


class NutrientsOut(BaseModel):
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float


class MealCalcItemOut(BaseModel):
    food_id: int
    name: str
    grams: float
    factor: float | None = None
    nutrients: NutrientsOut
    incomplete_data: bool
    error: str | None = None


class MealCalcResponse(BaseModel):
    totals: NutrientsOut
    incomplete_data: bool
    items: list[MealCalcItemOut]


class AdminFoodCreateIn(BaseModel):
    category_id: int | None = None
    category_name: str | None = None
    category_name_ro: str | None = None

    subcategory_id: int | None = None
    subcategory_name: str | None = None
    subcategory_name_ro: str | None = None

    food_description: str = Field(min_length=1, max_length=255)
    food_description_ro: str | None = Field(default=None, max_length=255)
    quantity: float | None = None
    measure: str | None = Field(default=None, max_length=255)
    wt_g: float = Field(gt=0)
    ener_kcal: float
    prot_g: float
    carbo_g: float
    fat_g: float
    fiber_g: float

    @model_validator(mode="after")
    def validate_refs(self) -> "AdminFoodCreateIn":
        has_category_id = self.category_id is not None
        has_category_name = bool(self.category_name and self.category_name.strip())
        if not has_category_id and not has_category_name:
            raise ValueError("Provide category_id or category_name")

        has_subcategory_id = self.subcategory_id is not None
        has_subcategory_name = bool(self.subcategory_name and self.subcategory_name.strip())
        if not has_subcategory_id and not has_subcategory_name:
            raise ValueError("Provide subcategory_id or subcategory_name")

        return self


class AdminFoodResponse(BaseModel):
    da_code: int
    food: FoodOut
