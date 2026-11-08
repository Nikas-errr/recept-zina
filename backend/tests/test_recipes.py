
SEARCH_URL = "/api/recipes/search"


def test_empty_ingredients_returns_422(client):
    response = client.post(SEARCH_URL, json={"ingredients": [], "avoid": []})

    assert response.status_code == 422


def test_more_than_four_ingredients_returns_422(client):
    response = client.post(
        SEARCH_URL,
        json={"ingredients": ["milk", "egg", "beef", "rice", "salt"]},
    )

    assert response.status_code == 422


def test_unknown_slug_returns_clear_400(client):
    response = client.post(SEARCH_URL, json={"ingredients": ["unicorn-meat"]})

    assert response.status_code == 400
    assert "unicorn-meat" in response.json()["message"]
