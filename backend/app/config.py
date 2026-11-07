"""Настройки проекта.

Все «адреса и числа» собраны в одном месте: если понадобится поменять
адрес TheMealDB или лимит рецептов, правится только этот файл, а не весь код.
"""

import os

from dotenv import load_dotenv

# load_dotenv() читает файл .env (если он есть) и кладёт его значения
# в переменные окружения. Самого .env в репозитории нет — он в .gitignore;
# есть только шаблон .env.example, который копируют и заполняют под себя.
load_dotenv()

# Адрес TheMealDB. Бесплатный API (v1) работает без ключа.
THEMEALDB_URL = os.getenv("THEMEALDB_URL", "https://www.themealdb.com/api/json/v1/1")

# Ключ нужен только платному тарифу TheMealDB (v2). В коде ключей нет:
# если когда-нибудь появится, он придёт из .env, а не из исходников.
THEMEALDB_API_KEY = os.getenv("THEMEALDB_API_KEY", "")

# Сколько секунд ждём ответ TheMealDB, прежде чем считать его недоступным.
REQUEST_TIMEOUT = 10

# Максимум рецептов в ответе (по ТЗ — не больше 5).
MAX_RESULTS = 5

# Допустимые значения параметра furnitureType у GET /api/ingredients.
# oven добавлен по просьбе фронтендера (у него на сайте есть вкладка
# «духовка»); пока у oven нет своих продуктов — вкладка вернёт пустой список.
ALLOWED_FURNITURE_TYPES = ("refrigerator", "wardrobe", "oven")

# --- Авторизация ---
# Секрет, которым подписываются JWT-токены. В .env.example есть поле
# AUTH_SECRET: на публике обязательно поставить туда своё случайное
# значение, иначе кто угодно сможет подделывать токены.
AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-secret-change-me-before-deploy")

# Сколько секунд живёт токен после входа (неделя).
AUTH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600
