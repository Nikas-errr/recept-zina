
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "ingredients.json"

MAX_CANDIDATES = 15


def load_ingredients() -> list[dict]:
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def clean_slug_list(values) -> list[str]:
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
    return " ".join((text or "").strip().lower().replace("_", " ").split())


def names_match(first: str, second: str) -> bool:
    first = normalize_name(first)
    second = normalize_name(second)
    return bool(first) and bool(second) and (first in second or second in first)


def recipe_ingredient_names(meal: dict) -> list[str]:
    names = []
    for number in range(1, 21):
        name = normalize_name(meal.get(f"strIngredient{number}") or "")
        if name:
            names.append(name)
    return names


def is_avoided(recipe_names: list[str], avoid_names: list[str]) -> bool:
    return any(
        names_match(avoid_name, recipe_name)
        for avoid_name in avoid_names
        for recipe_name in recipe_names
    )


def matched_ingredients_count(selected_names: list[str], recipe_names: list[str]) -> int:
    return sum(
        1
        for selected in selected_names
        if any(names_match(selected, recipe_name) for recipe_name in recipe_names)
    )


def split_instructions(text: str) -> list[str]:
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
