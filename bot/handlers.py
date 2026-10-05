"""Обработчики команд Telegram-бота BotPulse."""

from __future__ import annotations

import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .ai import ask_ai, get_ai_config
from .checkers import get_checker
from .config import ADMIN_IDS, CHECKS_EXAMPLE, load_checks

# --- Команды ---

HELP_TEXT = """BotPulse — бот для проверки балансов и статуса сервисов

Команды:
/start — приветствие
/help — эта справка
/checks — список настроенных проверок
/check <name> — выполнить одну проверку
/check_all — выполнить все проверки
/ai <вопрос> — задать вопрос AI (нужен API-ключ)
/config_example — показать пример конфигурации проверок
/status — статус AI-модуля

Типы проверок:
• VPN — баланс и статус VPN-подписок (3X-UI, Outline, Marzban)
• Crypto — баланс криптокошельков (BTC, ETH, BSC, TRX)
• API Service — баланс API-ключей (OpenAI, Gemini, DeepSeek и др.)
• Universal — любой HTTP-API запрос

Настройка: отредактируйте data/checks.json (см. /config_example)
"""


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "BotPulse — бот для проверки балансов и статуса сервисов.\n\n"
        "Введите /help для списка команд."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def cmd_checks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checks = load_checks()
    if not checks:
        await update.message.reply_text(
            "Проверки не настроены.\n"
            "Создайте data/checks.json (см. /config_example)."
        )
        return

    lines = ["Настроенные проверки:\n"]
    for i, c in enumerate(checks, 1):
        lines.append(f"{i}. {c.name} ({c.check_type})")
        if c.description:
            lines.append(f"   {c.description}")
    await update.message.reply_text("\n".join(lines))


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /check <name>")
        return

    name = " ".join(context.args)
    checks = load_checks()
    target = next((c for c in checks if c.name == name), None)

    if not target:
        await update.message.reply_text(f"Проверка '{name}' не найдена. /checks — список.")
        return

    await _run_check(update, target)


async def cmd_check_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checks = load_checks()
    if not checks:
        await update.message.reply_text("Проверки не настроены. /config_example — пример.")
        return

    await update.message.reply_text(f"Запускаю {len(checks)} проверок...")

    results = []
    for c in checks:
        checker_cls = get_checker(c.check_type)
        checker = checker_cls()
        result = await checker.check(c)
        results.append((c.name, result))

    lines = ["Результаты проверок:\n"]
    for name, res in results:
        status = "OK" if res.get("ok") else "FAIL"
        value = res.get("value") or res.get("balance") or res.get("raw", "")
        error = res.get("error", "")
        line = f"[{status}] {name}"
        if value:
            line += f": {value}"
        if error:
            line += f" — {error}"
        lines.append(line)

    await update.message.reply_text("\n".join(lines))


async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        config = get_ai_config()
        if config["configured"]:
            await update.message.reply_text(
                f"AI настроен: {config['provider']} / {config['model']}\n"
                "Использование: /ai <ваш вопрос>"
            )
        else:
            await update.message.reply_text(
                "AI не настроен.\n"
                "Укажите в .env:\n"
                "AI_PROVIDER=gemini\n"
                "AI_API_KEY=ваш_ключ\n"
                "AI_MODEL=gemini-2.0-flash"
            )
        return

    question = " ".join(context.args)
    await update.message.reply_text("Думаю...")

    # Собираем контекст из последних проверок
    context_text = ""
    checks = load_checks()
    if checks:
        context_lines = []
        for c in checks[:5]:
            checker_cls = get_checker(c.check_type)
            checker = checker_cls()
            result = await checker.check(c)
            status = "OK" if result.get("ok") else "FAIL"
            value = result.get("value") or result.get("balance") or ""
            context_lines.append(f"{c.name}: {status} {value}")
        context_text = "\n".join(context_lines)

    answer = await ask_ai(question, context_text)
    await update.message.reply_text(answer[:4096])


async def cmd_config_example(update: Update, context: ContextTypes.DEFAULT_TYPE):
    example = """Пример data/checks.json:

{
  "checks": [
    {
      "name": "OpenAI Balance",
      "check_type": "api_service",
      "description": "openai",
      "token": "sk-..."
    },
    {
      "name": "BTC Wallet",
      "check_type": "crypto",
      "address": "bc1q...",
      "currency": "BTC"
    },
    {
      "name": "VPN Panel",
      "check_type": "vpn",
      "url": "https://vpn.example.com/api/me",
      "token": "your-token"
    },
    {
      "name": "Custom API",
      "check_type": "universal",
      "url": "https://api.example.com/balance",
      "json_path": "data.balance",
      "headers": {"X-API-Key": "key123"}
    }
  ]
}"""
    await update.message.reply_text(f"```\n{example}\n```", parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = get_ai_config()
    checks = load_checks()

    lines = [
        "Статус BotPulse:",
        f"Проверок настроено: {len(checks)}",
        f"AI-модуль: {'настроен' if config['configured'] else 'не настроен'}",
    ]
    if config["configured"]:
        lines.append(f"Провайдер: {config['provider']}")
        lines.append(f"Модель: {config['model']}")
        lines.append(f"Base URL: {config['base_url']}")

    await update.message.reply_text("\n".join(lines))


async def _run_check(update: Update, config):
    """Выполняет одну проверку и отправляет результат."""
    checker_cls = get_checker(config.check_type)
    checker = checker_cls()
    result = await checker.check(config)

    lines = [f"Проверка: {config.name}"]
    status = "OK" if result.get("ok") else "FAIL"
    lines.append(f"Статус: {status}")

    if result.get("value") is not None:
        lines.append(f"Значение: {result['value']}")
    if result.get("balance") is not None:
        lines.append(f"Баланс: {result['balance']}")
    if result.get("address"):
        lines.append(f"Адрес: {result['address']}")
    if result.get("currency"):
        lines.append(f"Валюта: {result['currency']}")
    if result.get("error"):
        lines.append(f"Ошибка: {result['error']}")

    await update.message.reply_text("\n".join(lines))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений — пересылка в AI."""
    text = update.message.text
    if not text:
        return

    config = get_ai_config()
    if config["configured"]:
        await update.message.reply_text("Думаю...")
        answer = await ask_ai(text)
        await update.message.reply_text(answer[:4096])
    else:
        await update.message.reply_text(
            "Введите команду (/help — справка) или настройте AI (/status)"
        )


def setup_handlers(app: Application):
    """Регистрирует все обработчики команд."""
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("checks", cmd_checks))
    app.add_handler(CommandHandler("check", cmd_check))
    app.add_handler(CommandHandler("check_all", cmd_check_all))
    app.add_handler(CommandHandler("ai", cmd_ai))
    app.add_handler(CommandHandler("config_example", cmd_config_example))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
