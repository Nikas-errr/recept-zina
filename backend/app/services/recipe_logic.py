"""Логика работы с рецептами — без походов в интернет.

Здесь живёт «математика» проекта: чтение каталога, очистка данных,
сравнение ингредиентов, фильтрация по avoid и разбиение инструкции
на шаги. Все функции можно проверить тестами без сети.
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "ingredients.json"

MAX_CANDIDATES = 15


def load_ingredients() -> list[dict]:
    """Читает каталог продуктов из data/ingredients.json."""
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def clean_slug_list(values) -> list[str]:
    """Очищает список slug-ов: пробелы, регистр, пустые строки, дубли."""
    if not isinstance(values, list):
        raise ValueError("Нужно передать список продуктов")

    cleaned = []
    for item in values:
        if not isinstance(item, str):
            raise ValueError("Каждый продукт должен быть строкой")

        slug = " ".join(item.strip().lower().split())
        if slug:
            cleaned.append(slug)

    return list(dict.fromkeys(cleaned))


def normalize_name(text: str) -> str:
    """Приводит название продукта к единому виду для сравнения."""
    return " ".join((text or "").strip().lower().replace("_", " ").split())


def names_match(first: str, second: str) -> bool:
    """Считает названия совпадающими, если одно содержится в другом.

    Нужно, чтобы «milk» совпал и с «Milk», и с «Whole Milk» из рецепта.
    """
    first = normalize_name(first)
    second = normalize_name(second)
    return bool(first) and bool(second) and (first in second or second in first)


def recipe_ingredient_names(meal: dict) -> list[str]:
    """Собирает непустые названия ингредиентов из ответа TheMealDB (strIngredient1..20)."""
    names = []
    for number in range(1, 21):
        name = normalize_name(meal.get(f"strIngredient{number}") or "")
        if name:
            names.append(name)
    return names


def is_avoided(recipe_names: list[str], avoid_names: list[str]) -> bool:
    """True, если в рецепте есть хоть один нежелательный продукт."""
    return any(
        names_match(avoid_name, recipe_name)
        for avoid_name in avoid_names
        for recipe_name in recipe_names
    )


def matched_ingredients_count(selected_names: list[str], recipe_names: list[str]) -> int:
    """Считает, сколько выбранных пользователем продуктов есть в рецепте."""
    return sum(
        1
        for selected in selected_names
        if any(names_match(selected, recipe_name) for recipe_name in recipe_names)
    )


def split_instructions(text: str) -> list[str]:
    """Разбивает сплошной текст инструкции на отдельные шаги."""
    text = (text or "").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if len(lines) > 1:
        return lines

    sentences = []
    for part in text.replace("! ", ". ").replace("? ", ". ").split("."):
        part = part.strip()
        if part:
            sentences.append(part + ".")

    return sentences or ["Инструкция для этого блюда не указана."]


def build_recipe(meal: dict) -> dict:
    """Превращает ответ lookup.php в рецепт нашего формата.

    TheMealDB отдаёт ингредиенты в 20 парах полей strIngredient1..20 и
    strMeasure1..20; пустые пары пропускаем.
    """
    ingredients = []
    for number in range(1, 21):
        name = (meal.get(f"strIngredient{number}") or "").strip()
        amount = (meal.get(f"strMeasure{number}") or "").strip()
        if name:
            ingredients.append(
                {"name": name, "amount": amount or "Количество не указано"}
            )

    return {
        "id": str(meal.get("idMeal", "")),
        "title": meal.get("strMeal") or "Название не указано",
        "imageUrl": meal.get("strMealThumb"),
        "ingredients": ingredients,
        "steps": split_instructions(meal.get("strInstructions") or ""),
    }
