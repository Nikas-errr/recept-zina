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
    furniture_type: str | None = Query(default=None, alias="furnitureType"),
    search: str | None = Query(default=None),
):
    ingredients = load_ingredients()

    if furniture_type is not None:
        if furniture_type not in config.ALLOWED_FURNITURE_TYPES:
            raise HTTPException(
                status_code=422,
                detail="furnitureType должен быть одним из: "
                + ", ".join(config.ALLOWED_FURNITURE_TYPES),
            )
        ingredients = [
            item for item in ingredients if item.get("furnitureType") == furniture_type
        ]

    if search:
        needle = search.strip().lower()
        ingredients = [
            item
            for item in ingredients
            if needle in item["slug"].lower() or needle in item["name"].lower()
        ]

        def suggestion_rank(item: dict) -> tuple[int, str]:
            name = item["name"].lower()
            starts = name.startswith(needle) or item["slug"].lower().startswith(needle)
            return (0 if starts else 1, name)

        ingredients = sorted(ingredients, key=suggestion_rank)

    return {"data": ingredients}
