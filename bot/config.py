"""Конфигурация бота. Все значения берутся из переменных окружения (.env)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

# --- Telegram ---
BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- AI ---
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "")  # gemini, openai, custom
AI_API_KEY: str = os.getenv("AI_API_KEY", "")
AI_BASE_URL: str = os.getenv("AI_BASE_URL", "")
AI_MODEL: str = os.getenv("AI_MODEL", "")

# --- Checks data file ---
CHECKS_FILE: str = os.getenv("CHECKS_FILE", "data/checks.json")
CHECKS_EXAMPLE: str = "data/checks.example.json"

# --- Admin ---
ADMIN_IDS: list[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]


@dataclass
class CheckConfig:
    """Описание одной проверки из JSON-конфига."""

    name: str
    check_type: str  # vpn, crypto, api_service, universal
    url: str = ""
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    json_path: str = ""  # путь к значению в JSON-ответе, напр. "data.balance"
    token: str = ""  # токен/API-ключ для конкретного сервиса
    address: str = ""  # адрес кошелька (для crypto)
    currency: str = ""  # валюта (для crypto)
    description: str = ""


def load_checks() -> list[CheckConfig]:
    """Загружает конфигурацию проверок из JSON-файла."""
    path = Path(CHECKS_FILE)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CheckConfig(**item) for item in data.get("checks", [])]
