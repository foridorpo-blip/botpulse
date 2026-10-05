"""Чекер криптокошельков: баланс по адресу через публичные API."""

from __future__ import annotations

from typing import Any

import httpx


class CryptoChecker:
    """Проверка баланса криптокошельков.

    Поддерживаемые валюты (определяются по полю currency в конфиге):
    - BTC: blockchain.info API
    - ETH: etherscan.io API (нужен API-ключ в поле token)
    - BSC: bscscan.com API (нужен API-ключ в поле token)
    - TRX (TRC20): trongrid.io API
    """

    async def check(self, config) -> dict[str, Any]:
        address = config.address
        currency = (config.currency or "").upper()

        if not address:
            return {"ok": False, "error": "Адрес кошелька не указан"}
        if not currency:
            return {"ok": False, "error": "Валюта не указана"}

        api_url, headers = self._build_request(currency, address, config.token)

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(api_url, headers=headers)

            if resp.status_code >= 400:
                return {"ok": False, "error": f"HTTP {resp.status_code}", "status_code": resp.status_code}

            data = resp.json()
            balance = self._extract_balance(currency, data)

            return {
                "ok": True,
                "status_code": resp.status_code,
                "address": address,
                "currency": currency,
                "balance": balance,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _build_request(self, currency: str, address: str, token: str) -> tuple[str, dict]:
        headers = {"Accept": "application/json"}
        if currency == "BTC":
            return f"https://blockchain.info/q/addressbalance/{address}", headers
        elif currency == "ETH":
            url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest"
            if token:
                url += f"&apikey={token}"
            return url, headers
        elif currency == "BSC":
            url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest"
            if token:
                url += f"&apikey={token}"
            return url, headers
        elif currency == "TRX":
            return f"https://apilist.tronscanapi.com/api/accountv2?address={address}", headers
        else:
            return f"https://blockchain.info/q/addressbalance/{address}", headers

    def _extract_balance(self, currency: str, data: dict) -> str | None:
        if currency in ("ETH", "BSC"):
            # Etherscan/BscScan: {"result": "balance_in_wei"}
            result = data.get("result")
            if result and result.isdigit():
                return f"{int(result) / 1e18:.6f}"
            return result
        elif currency == "TRX":
            # Tronscan: {"balance": 12345.67}
            balance = data.get("balance")
            if balance is not None:
                return str(balance)
            return None
        elif currency == "BTC":
            # blockchain.info: raw satoshis
            if isinstance(data, (int, float)):
                return f"{data / 1e8:.8f}"
            return str(data)
        return str(data)[:200]
