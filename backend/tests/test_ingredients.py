"""Тесты GET /api/ingredients. Интернет не нужен: читаем локальный JSON."""


def test_returns_only_refrigerator_items(client):
    response = client.get("/api/ingredients", params={"furnitureType": "refrigerator"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0
    # В ответе ровно три поля — без служебных mealDbName и furnitureType.
    assert all(set(item) == {"slug", "name", "image"} for item in data)


def test_search_is_case_insensitive(client):
    response = client.get(
        "/api/ingredients",
        params={"furnitureType": "refrigerator", "search": "МОЛ"},
    )

    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()["data"]]
    assert "milk" in slugs


def test_unknown_furniture_type_returns_422(client):
    response = client.get("/api/ingredients", params={"furnitureType": "fridge"})

    assert response.status_code == 422


def test_oven_type_is_accepted(client):
    # oven добавлен по просьбе фронтендера; пока у него нет продуктов,
    # но тип должен приниматься и отвечать пустым списком, а не 422.
    response = client.get("/api/ingredients", params={"furnitureType": "oven"})

    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_without_furniture_type_returns_whole_catalog(client):
    # Без furnitureType отдаётся весь каталог: обе вкладки (холодильник
    # и шкаф) могут показывать все продукты.
    fridge = client.get(
        "/api/ingredients", params={"furnitureType": "refrigerator"}
    ).json()["data"]
    wardrobe = client.get(
        "/api/ingredients", params={"furnitureType": "wardrobe"}
    ).json()["data"]
    everything = client.get("/api/ingredients").json()["data"]

    assert len(everything) == len(fridge) + len(wardrobe)
    slugs = {item["slug"] for item in everything}
    assert "chicken-breast" in slugs  # из холодильника
    assert "rice" in slugs  # из шкафа


def test_search_suggestions_are_sorted_prefix_first(client):
    # «мо»: Молоко, Морковь и Моцарелла НАЧИНАЮТСЯ с «мо» (по алфавиту),
    # дальше совпадения внутри слова по алфавиту: Кокосовое молоко, Лимон.
    response = client.get("/api/ingredients", params={"search": "мо"})

    slugs = [item["slug"] for item in response.json()["data"]]
    assert slugs[:5] == ["milk", "carrot", "mozzarella", "coconut-milk", "lemon"]
