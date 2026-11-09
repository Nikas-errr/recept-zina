
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Проверка, что сервер запущен"""
    return {"status": "ok"}
