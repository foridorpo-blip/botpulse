"""Чекер VPN-сервисов: проверка баланса и статуса подписки через панель/API."""

from __future__ import annotations

from typing import Any

import httpx


class VpnChecker:
    """Проверка VPN-сервисов.

    Поддерживает два режима:
    1. URL API панели (3X-UI, Outline, Marzban и др.) + токен
    2. Универсальный URL для кастомных панелей
    """

    async def check(self, config) -> dict[str, Any]:
        url = config.url
        if not url:
            return {"ok": False, "error": "URL панели VPN не указан"}

        headers = {"Accept": "application/json"}
        if config.token:
            headers["Authorization"] = f"Bearer {config.token}"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=headers)

            if resp.status_code >= 400:
                return {"ok": False, "error": f"HTTP {resp.status_code}", "status_code": resp.status_code}

            data = resp.json()

            # Пытаемся найти баланс/статус по json_path или автоматически
            value = None
            if config.json_path:
                from .universal import _extract_path
                value = _extract_path(data, config.json_path)
            else:
                # Автопоиск общих полей
                for key in ("balance", "remaining", "days_left", "status", "active", "data_limit", "used"):
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
