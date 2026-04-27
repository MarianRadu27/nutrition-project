from __future__ import annotations

import os
from typing import Any

import pymysql
from dotenv import load_dotenv

load_dotenv()


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except (TypeError, ValueError):
        return default


def get_db_config() -> dict[str, Any]:
    return {
        "host": _env_str("DB_HOST", "127.0.0.1"),
        "port": _env_int("DB_PORT", 3307),
        "user": _env_str("DB_USER", "nutrition"),
        "password": _env_str("DB_PASSWORD", "nutritionpass"),
        "database": _env_str("DB_NAME", "nutrition"),
        "charset": "utf8mb4",
        "autocommit": False,
        "cursorclass": pymysql.cursors.DictCursor,
    }


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(**get_db_config())


def get_admin_token() -> str:
    return _env_str("ADMIN_TOKEN", "change-me-local-admin-token")


def get_frontend_origins() -> list[str]:
    raw = _env_str("FRONTEND_ORIGIN", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
