"""Универсальный HTTP-чекер: запрос по URL, извлечение значения по JSON-пути."""

from __future__ import annotations

import json
from typing import Any

import httpx


class UniversalChecker:
    """Универсальная проверка любого HTTP-API.

    Делает запрос и извлекает значение по JSON-пути (data.balance и т.д.).
    """

    async def check(self, config) -> dict[str, Any]:
        url = config.url
        if not url:
            return {"ok": False, "error": "URL не указан"}

        headers = config.headers or {}
        if config.token:
            headers.setdefault("Authorization", f"Bearer {config.token}")

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.request(config.method or "GET", url, headers=headers)
            if resp.status_code >= 400:
                return {"ok": False, "error": f"HTTP {resp.status_code}", "status_code": resp.status_code}

            if not config.json_path:
                return {
                    "ok": True,
                    "status_code": resp.status_code,
                    "raw": resp.text[:500],
                }

            data = resp.json()
            value = _extract_path(data, config.json_path)
            return {
                "ok": True,
                "status_code": resp.status_code,
                "value": value,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def _extract_path(data: Any, path: str) -> Any:
    """Извлекает значение из dict по точечному пути: data.balance -> data['balance']."""
    current = data
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None
    return current
