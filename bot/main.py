"""Точка входа BotPulse — Telegram-бот для проверки балансов.

Запуск:
    python -m bot.main

Требуется .env с TELEGRAM_BOT_TOKEN.
Опционально: AI_PROVIDER, AI_API_KEY, AI_MODEL, AI_BASE_URL.
"""

from __future__ import annotations

import logging
import sys

from telegram.ext import Application

from .config import BOT_TOKEN
from .handlers import setup_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN:
        print(
            "Ошибка: TELEGRAM_BOT_TOKEN не указан.\n"
            "Создайте .env файл (см. .env.example) и укажите токен бота.\n"
            "Получить токен: @BotFather в Telegram",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("Запуск BotPulse...")
    app = Application.builder().token(BOT_TOKEN).build()
    setup_handlers(app)

    logger.info("BotPulse запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
