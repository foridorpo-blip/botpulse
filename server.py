"""BotPulse — backend API server.

Provides:
- /api/chat — прокси к Gemini API (OpenAI-совместимый эндпоинт)
- /api/status — статус лицензии API-ключа
- /api/activate — активация API-ключа
- /api/renew — продление API-ключа
- /api/models — список доступных моделей
- Статические файлы (index.html, style.css, script.js)

Лицензия: 6 дней работы → 7 дней блокировки → продление или новый ключ.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".")

# === Конфигурация ===
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash"]
DEFAULT_MODEL = "gemini-3.5-flash"

# Периоды лицензии
ACTIVE_DAYS = 6   # 6 дней ключ работает
LOCKED_DAYS = 7   # 7 дней ключ заблокирован

# Runtime directory — внешние файлы (proxy, CA bundle, license)
RUNTIME_DIR = Path(os.environ.get("BOTPULSE_RUNTIME_DIR", str(Path(__file__).parent / "runtime")))
LICENSE_FILE = RUNTIME_DIR / "license.json"
PROXY_URL_FILE = RUNTIME_DIR / ".proxy_url"
CA_BUNDLE_FILE = RUNTIME_DIR / ".ca-bundle.pem"

# === Лицензия ===

def load_license() -> dict | None:
    if LICENSE_FILE.exists():
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    return None


def save_license(data: dict) -> None:
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_license_status() -> dict:
    lic = load_license()
    if not lic:
        return {
            "status": "inactive",
            "message": "API-ключ не активирован. Нажмите «Активировать».",
            "can_activate": True,
            "can_renew": False,
        }

    activated = datetime.fromisoformat(lic["activated"])
    now = datetime.now()
    expiry = activated + timedelta(days=ACTIVE_DAYS)
    lock_end = expiry + timedelta(days=LOCKED_DAYS)

    if now < expiry:
        remaining = expiry - now
        days = remaining.days
        hours = remaining.seconds // 3600
        return {
            "status": "active",
            "message": f"Активен. Осталось {days} дн. {hours} ч.",
            "remaining_days": days,
            "can_activate": False,
            "can_renew": False,
        }
    elif now < lock_end:
        remaining = lock_end - now
        days = remaining.days
        return {
            "status": "locked",
            "message": f"Заблокирован. До продления: {days} дн.",
            "remaining_days": days,
            "can_activate": False,
            "can_renew": False,
        }
    else:
        return {
            "status": "expired",
            "message": "Срок истёк. Можно продлить или создать новый ключ.",
            "can_activate": False,
            "can_renew": True,
        }


# === Эндпоинты ===

@app.route("/api/status")
def api_status():
    return jsonify(get_license_status())


@app.route("/api/activate", methods=["POST"])
def api_activate():
    status = get_license_status()
    if status["status"] == "active":
        return jsonify({"error": "Ключ уже активен"}), 400
    if status["status"] == "locked":
        return jsonify({"error": "Ключ заблокирован, продление невозможно"}), 400
    save_license({"activated": datetime.now().isoformat()})
    return jsonify({
        "status": "active",
        "message": "API-ключ активирован на 6 дней",
    })


@app.route("/api/renew", methods=["POST"])
def api_renew():
    status = get_license_status()
    if not status["can_renew"]:
        return jsonify({"error": status["message"]}), 400
    save_license({"activated": datetime.now().isoformat()})
    return jsonify({
        "status": "active",
        "message": "API-ключ продлён на 6 дней",
    })


@app.route("/api/models")
def api_models():
    return jsonify({"models": MODELS, "default": DEFAULT_MODEL})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    status = get_license_status()
    if status["status"] != "active":
        return jsonify({"error": status["message"]}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Тело запроса пустое"}), 400

    model = data.get("model", DEFAULT_MODEL)
    messages = data.get("messages", [])

    if model not in MODELS:
        return jsonify({"error": f"Модель '{model}' недоступна. Доступные: {', '.join(MODELS)}"}), 400

    if not messages:
        return jsonify({"error": "Сообщения не переданы"}), 400

    # Запрос к Gemini через OpenAI-совместимый эндпоинт
    # API-ключ injected через прокси (Authorization: Bearer <key>)
    import requests as req_lib

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7,
    }

    try:
        # Build proxy from runtime file or env
        proxy_url = ""
        if PROXY_URL_FILE.exists():
            proxy_url = PROXY_URL_FILE.read_text().strip()
        if not proxy_url:
            proxy_url = os.environ.get("HTTPS_PROXY", "")
        proxies = {"https": proxy_url, "http": proxy_url} if proxy_url else None

        # API key — direct env var (for cloned projects) or injected via proxy
        api_key = os.environ.get("GEMINI_API_KEY", "")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # SSL verification — configurable via env (default: verify)
        verify_ssl = os.environ.get("VERIFY_SSL", "true").lower() == "true"
        if verify_ssl and CA_BUNDLE_FILE.exists():
            verify_ssl = str(CA_BUNDLE_FILE)

        resp = req_lib.post(
            GEMINI_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
            proxies=proxies,
            verify=verify_ssl,
        )
        result = resp.json()

        # Handle dict or list response
        if isinstance(result, list):
            # Some APIs return a list
            if result and isinstance(result[0], dict):
                content = result[0].get("message", {}).get("content", "") or result[0].get("content", "")
                if content:
                    return jsonify({"response": content, "model": model, "status": "ok"})
            return jsonify({"error": "Неожиданный формат ответа", "detail": str(result)[:500]}), 500

        if isinstance(result, dict):
            # Check for error
            if "error" in result:
                err = result["error"]
                err_msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                return jsonify({"error": f"Ошибка AI: {err_msg}", "detail": str(result)[:500]}), 502

            choices = result.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                return jsonify({"response": content, "model": model, "status": "ok"})

        return jsonify({"error": "Пустой ответ от AI", "detail": str(result)[:500]}), 500
    except req_lib.exceptions.HTTPError as e:
        return jsonify({
            "error": f"Ошибка AI API (HTTP {e.response.status_code})",
            "detail": e.response.text[:500],
        }), 502
    except Exception as e:
        return jsonify({"error": f"Ошибка: {e}"}), 500


# === Статические файлы ===

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
