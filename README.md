# BotPulse

Telegram-бот для проверки балансов и статуса сервисов с интеграцией AI.

## Возможности

- **VPN-сервисы** — проверка баланса и статуса подписок (3X-UI, Outline, Marzban и др.)
- **Криптокошельки** — баланс BTC, ETH, BSC, TRX по адресу
- **API-сервисы** — баланс API-ключей OpenAI, Gemini, DeepSeek и др.
- **Универсальные проверки** — любой HTTP-API запрос с извлечением данных по JSON-пути
- **AI-модуль** — задаёте любой API-ключ от любого провайдера (Gemini, OpenAI, DeepSeek, OpenRouter, кастомный)

## Быстрый старт

### 1. Установка

```bash
git clone https://github.com/foridorpo-blip/botpulse.git
cd botpulse
pip install -r requirements.txt
```

### 2. Настройка

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather

# AI (опционально)
AI_PROVIDER=gemini
AI_API_KEY=ваш_ключ
AI_MODEL=gemini-2.0-flash
```

### 3. Настройка проверок

Скопируйте пример конфигурации:

```bash
cp data/checks.example.json data/checks.json
```

Отредактируйте `data/checks.json` — добавьте свои сервисы.

### 4. Запуск

```bash
python -m bot.main
```

## AI-модуль

AI-модуль поддерживает любого провайдера через OpenAI-совместимый API:

| Провайдер | AI_PROVIDER | AI_MODEL (пример) |
|-----------|-------------|-------------------|
| Gemini | `gemini` | `gemini-2.0-flash` |
| OpenAI | `openai` | `gpt-4o-mini` |
| DeepSeek | `deepseek` | `deepseek-chat` |
| OpenRouter | `openrouter` | `openrouter/auto` |
| Кастомный | `custom` | любой |

Для кастомного провайдера укажите `AI_BASE_URL` вручную.

Поле API-ключа пустое по умолчанию — вы вводите ключ любого провайдера.

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие |
| `/help` | Справка |
| `/checks` | Список настроенных проверок |
| `/check <name>` | Выполнить одну проверку |
| `/check_all` | Выполнить все проверки |
| `/ai <вопрос>` | Задать вопрос AI |
| `/status` | Статус AI-модуля |
| `/config_example` | Пример конфигурации |

## Безопасность

- Никогда не коммитьте `.env` и `data/checks.json` с реальными ключами
- API-ключи хранятся только в `.env` локально
- `.gitignore` уже исключает чувствительные файлы

## Лицензия

MIT
