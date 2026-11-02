"""Роутер GET /api/health — простая проверка, что сервер запущен."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Пока этот адрес отвечает — проект жив и работает."""
    return {"status": "ok"}
