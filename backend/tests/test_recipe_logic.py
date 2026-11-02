"""Тесты чистых функций recipe_logic — самые быстрые, без API и сети."""

from app.services import recipe_logic


def test_clean_slug_list_strips_and_dedupes():
    result = recipe_logic.clean_slug_list(["  milk ", "MILK", "", "  egg "])

    assert result == ["milk", "egg"]


def test_split_instructions_breaks_text_into_steps():
    steps = recipe_logic.split_instructions("Boil water. Add pasta. Cook for 10 minutes.")

    assert len(steps) == 3
    assert steps[0] == "Boil water."


def test_is_avoided_finds_milk_among_ingredients():
    assert recipe_logic.is_avoided(["milk", "sugar"], ["milk"]) is True
    assert recipe_logic.is_avoided(["water", "sugar"], ["milk"]) is False
