"""Общие фикстуры для тестов."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """«Клиент», который дёргает наше API без запуска настоящего сервера."""
    return TestClient(app)
