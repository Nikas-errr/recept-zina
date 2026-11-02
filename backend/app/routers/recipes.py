"""Роутер POST /api/recipes/search — подбор рецептов по продуктам.

Роутер — «диспетчер»: принимает запрос, проверяет slug-и по каталогу,
раздаёт работу сервисам (mealdb ходит в интернет, recipe_logic считает)
и собирает итоговый ответ. Сам по себе в интернет не ходит.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import config
from app.schemas import ErrorResponse, RecipeSearchRequest, RecipeSearchResponse
from app.services import mealdb, recipe_logic

router = APIRouter()

# Подсказки для документации /docs: какие ещё коды может вернуть endpoint.
responses = {
    400: {"model": ErrorResponse, "description": "Неизвестный продукт"},
    503: {"model": ErrorResponse, "description": "TheMealDB недоступен"},
}


def empty_result() -> dict:
    """Единообразный ответ «ничего не нашли» (код всё равно 200)."""
    return {"recipes": [], "count": 0, "message": "Подходящие рецепты не найдены"}


@router.post(
    "/recipes/search",
    response_model=RecipeSearchResponse,
    responses=responses,
)
def search_recipes(request: RecipeSearchRequest):
    # Каталог вида {"chicken-breast": {...}, ...} — так удобнее искать по slug.
    catalog = {item["slug"]: item for item in recipe_logic.load_ingredients()}

    # Slug-и уже очищены от пробелов и дублей — это сделала схема
    # RecipeSearchRequest, вызвав recipe_logic.clean_slug_list.
    unknown = [
        slug for slug in request.ingredients + request.avoid if slug not in catalog
    ]
    if unknown:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Неизвестные продукты: "
                + ", ".join(unknown)
                + ". Полный список смотрите в GET /api/ingredients."
            },
        )

    # Превращаем slug-и в названия TheMealDB. Выбранные продукты и avoid
    # обрабатываем раздельно: avoid — чёрный список, а не «то, что ищем».
    selected_names = [catalog[slug]["mealDbName"] for slug in request.ingredients]
    avoid_names = [catalog[slug]["mealDbName"] for slug in request.avoid]

    try:
        # Шаг 1: ищем блюда по каждому продукту и сливаем результаты в словарь —
        # дубликаты по idMeal при этом исчезают сами.
        found = {}
        for name in selected_names:
            for meal in mealdb.get_meals_by_ingredient(name):
                meal_id = meal.get("idMeal")
                if meal_id:
                    found[meal_id] = meal

        if not found:
            return empty_result()

        # Шаг 2: подробности запрашиваем не у всех найденных блюд (их могут
        # быть десятки), а у первых MAX_CANDIDATES — иначе запрос висит слишком
        # долго.
        scored = []
        for meal_id in list(found)[: recipe_logic.MAX_CANDIDATES]:
            meal = mealdb.get_meal_details(meal_id)
            if not meal:
                continue

            recipe_names = recipe_logic.recipe_ingredient_names(meal)

            # Шаг 3: в рецепте есть продукт из avoid — выбрасываем целиком.
            if recipe_logic.is_avoided(recipe_names, avoid_names):
                continue

            # Шаг 4: считаем, сколько выбранных продуктов реально есть в
            # рецепте, чтобы сверху оказались блюда с большим числом совпадений.
            matched = recipe_logic.matched_ingredients_count(
                selected_names, recipe_names
            )
            scored.append((matched, recipe_logic.build_recipe(meal)))

        # Шаг 5: сортируем по числу совпадений и оставляем максимум 5 рецептов.
        scored.sort(key=lambda pair: pair[0], reverse=True)
        recipes = [recipe for _, recipe in scored[: config.MAX_RESULTS]]

    except mealdb.MealDbUnavailable:
        # TheMealDB не ответил. По ТЗ отдаём понятный JSON с кодом 503,
        # а не traceback с кодом 500.
        return JSONResponse(
            status_code=503,
            content={"message": "Сервис рецептов временно недоступен, попробуйте позже"},
        )

    if not recipes:
        # Например, все кандидаты вылетели по avoid-фильтру.
        return empty_result()

    return {"recipes": recipes, "count": len(recipes), "message": "ok"}
