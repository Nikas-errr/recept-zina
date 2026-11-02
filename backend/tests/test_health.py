"""Тест GET /api/health."""


def test_health_answers_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
