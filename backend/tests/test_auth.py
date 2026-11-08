"""Тесты авторизации: регистрация, вход, /me.

База на время теста подменяется временной — настоящая data/users.db
не трогается.
"""

import pytest

from app import database

AUTH = "/api/auth"
EMAIL = "vasya@mail.ru"
PASSWORD = "super-secret-123"


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    """Временный файл базы вместо настоящего на время теста."""
    db_file = tmp_path / "users.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()
    return db_file


def test_register_login_and_me(fresh_db, client):
    r = client.post(f"{AUTH}/register", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["email"] == EMAIL
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    r = client.post(f"{AUTH}/register", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 400

    r = client.post(f"{AUTH}/login", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == EMAIL

    r = client.get(f"{AUTH}/me")
    assert r.status_code == 401


def test_login_with_wrong_password(fresh_db, client):
    client.post(f"{AUTH}/register", json={"email": EMAIL, "password": PASSWORD})

    r = client.post(f"{AUTH}/login", json={"email": EMAIL, "password": "wrong-pass-99"})

    assert r.status_code == 401
    assert r.json() == {"message": "Неверный email или пароль"}


def test_email_is_normalized(fresh_db, client):
    client.post(f"{AUTH}/register", json={"email": " VASYA@Mail.RU ", "password": PASSWORD})

    r = client.post(f"{AUTH}/login", json={"email": "vasya@mail.ru", "password": PASSWORD})

    assert r.status_code == 200


def test_short_password_rejected(fresh_db, client):
    r = client.post(f"{AUTH}/register", json={"email": EMAIL, "password": "коротко"})

    assert r.status_code == 422
