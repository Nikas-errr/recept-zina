"""Мини-база пользователей на SQLite (файл data/users.db).

SQLite — это обычный файл с таблицами, встроенный в Python: ничего
устанавливать не нужно. Мы договорились, что для учебного проекта этого
достаточно (на бесплатном Render база очищается при передеплое).

Внимание: исходное ТЗ запрещало базу данных и авторизацию — этот модуль
появился по решению команды, потому что фронтенд уже отправляет
email и пароль на POST /auth/login.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "users.db"


def get_connection() -> sqlite3.Connection:
    """Новое подключение к базе. row_factory — читать строки как словари."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Создаёт таблицу пользователей, если её ещё нет."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            )
            """
        )
