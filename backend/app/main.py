"""Точка входа: собирает приложение из роутеров и умеет запускать сервер.

Сам логики здесь нет — только «склейка»: создать FastAPI, включить CORS,
подключить роутеры.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.routers import auth, health, ingredients, recipes

app = FastAPI(
    title="Recept_zina",
    description="Подбор рецептов по продуктам из холодильника или шкафа.",
    version="1.0.0",
)

# CORS — разрешение для браузера (фронтенда) обращаться к этому API с другого
# адреса. Для разработки разрешаем всем — «*». ПЕРЕД ПУБЛИКАЦИЕЙ заменить
# «*» на точный адрес фронтенда, например: allow_origins=["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры. prefix="/api" добавляет /api ко всем их адресам сразу:
# health отвечает на /api/health, ingredients — на /api/ingredients и т.д.
app.include_router(health.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

# Создаём таблицу пользователей, если базы ещё нет (data/users.db).
database.init_db()


if __name__ == "__main__":
    # Позволяет запустить сервер командой «python -m app.main»,
    # но обычный способ из README удобнее: uvicorn app.main:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000)
