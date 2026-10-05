"""Чекер API-сервисов: баланс API-ключей различных провайдеров."""

from __future__ import annotations

from typing import Any

import httpx


class ApiServiceChecker:
    """Проверка баланса API-ключей провайдеров.

    Шаблоны для популярных провайдеров:
    - OpenAI: GET https://api.openai.com/v1/credits, Authorization: Bearer <key>
    - Gemini: GET https://generativelanguage.googleapis.com/v1beta/models?key=<key>
    - DeepSeek: GET https://api.deepseek.com/user/balance, Authorization: Bearer <key>
    - Любой другой: URL + headers из конфига
    """

    # Встроенные шаблоны
    TEMPLATES = {
        "openai": {
            "url": "https://api.openai.com/v1/credits",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        },
        "deepseek": {
            "url": "https://api.deepseek.com/user/balance",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models",
            "auth_header": "x-goog-api-key",
            "auth_prefix": "",
        },
    }

    async def check(self, config) -> dict[str, Any]:
        token = config.token or config.headers.get("Authorization", "").replace("Bearer ", "")

        if not token and not config.url:
            return {"ok": False, "error": "API-ключ или URL не указан"}

        # Если URL не задан, пытаемся использовать шаблон по описанию
        url = config.url
        headers = {"Accept": "application/json"}

        if not url:
            provider = (config.description or "").lower()
            for name, template in self.TEMPLATES.items():
                if name in provider:
                    url = template["url"]
                    auth_h = template["auth_header"]
                    auth_p = template["auth_prefix"]
                    headers[auth_h] = f"{auth_p}{token}"
                    break
        else:
            if config.token:
                headers["Authorization"] = f"Bearer {token}"
            headers.update(config.headers)

        if not url:
            return {"ok": False, "error": "Не удалось определить URL API. Укажите url в конфиге."}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=headers)

            if resp.status_code >= 400:
                return {"ok": False, "error": f"HTTP {resp.status_code}", "status_code": resp.status_code}

            data = resp.json()
            value = None

            if config.json_path:
                from .universal import _extract_path
                value = _extract_path(data, config.json_path)
            else:
                # Автопоиск баланса
                for key in ("balance", "total_balance", "credits", "amount", "data"):
                    if isinstance(data, dict) and key in data:
                        value = data[key]
                        break

            return {
                "ok": True,
                "status_code": resp.status_code,
                "value": value,
                "raw": str(data)[:300],
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
