"""Плагины проверки балансов: VPN, крипто, API-сервисы, универсальный HTTP."""

from .universal import UniversalChecker
from .vpn import VpnChecker
from .crypto import CryptoChecker
from .api_service import ApiServiceChecker

CHECKERS = {
    "universal": UniversalChecker,
    "vpn": VpnChecker,
    "crypto": CryptoChecker,
    "api_service": ApiServiceChecker,
}


def get_checker(check_type: str):
    """Возвращает класс чекера по типу."""
    return CHECKERS.get(check_type, UniversalChecker)
