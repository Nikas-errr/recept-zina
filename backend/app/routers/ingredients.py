"""Роутер GET /api/ingredients — каталог продуктов из локального JSON.

Никаких баз данных: каталог лежит в data/ingredients.json, а роутер
только фильтрует его по «шкафчику» и поисковому запросу.
"""

from fastapi import APIRouter, HTTPException, Query

from app import config
from app.schemas import IngredientsResponse
from app.services.recipe_logic import load_ingredients

router = APIRouter()


@router.get("/ingredients", response_model=IngredientsResponse)
def list_ingredients(
    furniture_type: str = Query(..., alias="furnitureType"),
    search: str | None = Query(default=None),
):
    # Проверяем furnitureType по списку из config.py. Ошибка валидации — 422.
    if furniture_type not in config.ALLOWED_FURNITURE_TYPES:
        raise HTTPException(
            status_code=422,
            detail="furnitureType должен быть одним из: "
            + ", ".join(config.ALLOWED_FURNITURE_TYPES),
        )

    ingredients = load_ingredients()

    # Шаг 1: оставляем только продукты выбранного «шкафчика».
    data = [
        item for item in ingredients if item.get("furnitureType") == furniture_type
    ]

    # Шаг 2: если передан search — регистронезависимый поиск по slug и name.
    if search:
        needle = search.strip().lower()
        data = [
            item
            for item in data
            if needle in item["slug"].lower() or needle in item["name"].lower()
        ]

    # В ответ попадут только slug, name, image — лишние поля (mealDbName
    # и furnitureType) FastAPI отрежет сам, потому что ответ проверяется
    # по схеме IngredientsResponse.
    return {"data": data}
