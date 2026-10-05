"""AI-модуль: универсальный клиент для любого LLM-провайдера.

Поддерживает любого провайдера через OpenAI-совместимый API:
- OpenAI (api.openai.com)
- Gemini (generativelanguage.googleapis.com) через OpenAI-совместимый эндпоинт
- DeepSeek, OpenRouter, Together AI, Ollama и любые другие OpenAI-совместимые API

Конфигурация:
  AI_PROVIDER — gemini, openai, deepseek, openrouter, custom (пусто = кастомный)
  AI_API_KEY  — API-ключ (любой провайдер)
  AI_BASE_URL — базовый URL (опционально, автоопределение по провайдеру)
  AI_MODEL    — название модели (опционально, дефолт по провайдеру)
"""

from __future__ import annotations

import os

import httpx

# Автоматические пресеты провайдеров
PROVIDER_PRESETS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "default_model": "gemini-2.0-flash",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/auto",
    },
}


def get_ai_config() -> dict:
    """Собирает конфигурацию AI из переменных окружения."""
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    api_key = os.getenv("AI_API_KEY", "").strip()
    base_url = os.getenv("AI_BASE_URL", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    # Если провайдер известен — подставляем пресет
    if provider in PROVIDER_PRESETS:
        preset = PROVIDER_PRESETS[provider]
        if not base_url:
            base_url = preset["base_url"]
        if not model:
            model = preset["default_model"]

    return {
        "provider": provider or "custom",
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "configured": bool(api_key and base_url and model),
    }


async def ask_ai(prompt: str, context: str = "") -> str:
    """Запрос к AI-модели через OpenAI-совместимый API.

    Args:
        prompt: Вопрос пользователя
        context: Дополнительный контекст (результаты проверок и т.д.)

    Returns:
        Ответ модели в виде строки
    """
    config = get_ai_config()

    if not config["configured"]:
        return (
            "AI не настроен. Укажите в .env:\n"
            "AI_PROVIDER=gemini  (или openai, deepseek, openrouter, custom)\n"
            "AI_API_KEY=ваш_ключ\n"
            "AI_MODEL=gemini-2.0-flash  (или любая модель)\n"
            "AI_BASE_URL=https://...  (опционально, авто для известных провайдеров)"
        )

    messages = []
    if context:
        messages.append({"role": "system", "content": f"Контекст:\n{context}"})
    messages.append({"role": "user", "content": prompt})

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config["model"],
                    "messages": messages,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
            )

        if resp.status_code >= 400:
            return f"Ошибка AI API (HTTP {resp.status_code}): {resp.text[:300]}"

        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "Пустой ответ")
        return "Пустой ответ от AI"
    except Exception as exc:
        return f"Ошибка при обращении к AI: {exc}"
