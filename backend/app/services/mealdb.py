"""Единственное место проекта, откуда ходят запросы в TheMealDB.

Модуль ничего не знает про правила поиска: только «спросить — отдать ответ».
Если внешний сервис не ответил, бросается исключение MealDbUnavailable,
и роутер превращает его в понятный ответ с кодом 503.
"""

import requests

from app import config


class MealDbUnavailable(Exception):
    """TheMealDB не ответил или ответил ошибкой."""


def _get(path: str, params: dict) -> dict:
    """Общий помощник: GET-запрос к TheMealDB с таймаутом и проверкой статуса."""
    try:
        response = requests.get(
            f"{config.THEMEALDB_URL}/{path}",
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        raise MealDbUnavailable("TheMealDB недоступен")


def get_meals_by_ingredient(meal_db_name: str) -> list[dict]:
    """Список блюд по одному продукту: /filter.php?i=..."""
    data = _get("filter.php", {"i": meal_db_name})
    return data.get("meals") or []


def get_meal_details(meal_id: str) -> dict | None:
    """Подробности одного блюда по его id: /lookup.php?i=..."""
    data = _get("lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    return meals[0] if meals else None
