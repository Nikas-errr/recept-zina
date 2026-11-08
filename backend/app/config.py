"""Настройки проекта.

Все «адреса и числа» собраны в одном месте: если понадобится поменять
адрес TheMealDB или лимит рецептов, правится только этот файл, а не весь код.
"""

import os

from dotenv import load_dotenv

load_dotenv()

THEMEALDB_URL = os.getenv("THEMEALDB_URL", "https://www.themealdb.com/api/json/v1/1")

THEMEALDB_API_KEY = os.getenv("THEMEALDB_API_KEY", "")

REQUEST_TIMEOUT = 10

MAX_RESULTS = 5

ALLOWED_FURNITURE_TYPES = ("refrigerator", "wardrobe", "oven")

AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-secret-change-me-before-deploy")

AUTH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600
