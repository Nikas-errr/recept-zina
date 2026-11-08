
import requests

from app import config


class MealDbUnavailable(Exception):
    pass


def _get(path: str, params: dict) -> dict:
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
    data = _get("filter.php", {"i": meal_db_name})
    return data.get("meals") or []


def get_meal_details(meal_id: str) -> dict | None:
    data = _get("lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    return meals[0] if meals else None
