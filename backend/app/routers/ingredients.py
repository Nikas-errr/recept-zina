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
    # furnitureType теперь НЕОБЯЗАТЕЛЕН. Без него отдаётся весь каталог —
    # так обе вкладки (и холодильник, и шкаф) могут показывать все продукты,
    # а поиск-подсказка ищет по всему списку сразу.
    # Если параметр передан — проверяем его по списку из config.py (422 при ошибке)
    # и оставляем только продукты выбранного «шкафчика».
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

    # Если передан search — регистронезависимый поиск по slug и name
    # (по нему фронт строит подсказки, пока пользователь печатает).
    if search:
        needle = search.strip().lower()
        ingredients = [
            item
            for item in ingredients
            if needle in item["slug"].lower() or needle in item["name"].lower()
        ]

        # Сортировка подсказок: сначала продукты, чьё имя или slug НАЧИНАЕТСЯ
        # с запроса («мо» → Молоко, Морковь), потом те, где запрос в середине
        # («лимон»). Внутри групп — по алфавиту. Кортеж (группа, имя) как раз
        # даёт такой порядок при обычной сортировке.
        def suggestion_rank(item: dict) -> tuple[int, str]:
            name = item["name"].lower()
            starts = name.startswith(needle) or item["slug"].lower().startswith(needle)
            return (0 if starts else 1, name)

        ingredients = sorted(ingredients, key=suggestion_rank)

    # В ответ попадут только slug, name, image — лишние поля (mealDbName
    # и furnitureType) FastAPI отрежет сам, потому что ответ проверяется
    # по схеме IngredientsResponse.
    return {"data": ingredients}
