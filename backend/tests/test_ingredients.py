

def test_returns_only_refrigerator_items(client):
    response = client.get("/api/ingredients", params={"furnitureType": "refrigerator"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0
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
    response = client.get("/api/ingredients", params={"furnitureType": "oven"})

    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_without_furniture_type_returns_whole_catalog(client):
    fridge = client.get(
        "/api/ingredients", params={"furnitureType": "refrigerator"}
    ).json()["data"]
    wardrobe = client.get(
        "/api/ingredients", params={"furnitureType": "wardrobe"}
    ).json()["data"]
    everything = client.get("/api/ingredients").json()["data"]

    assert len(everything) == len(fridge) + len(wardrobe)
    slugs = {item["slug"] for item in everything}
    assert "chicken-breast" in slugs
    assert "rice" in slugs


def test_search_suggestions_are_sorted_prefix_first(client):
    response = client.get("/api/ingredients", params={"search": "мо"})

    slugs = [item["slug"] for item in response.json()["data"]]
    assert slugs[:5] == ["milk", "carrot", "mozzarella", "coconut-milk", "lemon"]
