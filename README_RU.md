# Job Scraper

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Десктопный агрегатор вакансий с панелью на **Flet**. Собирает объявления с **hh.ru**, **Habr Career**, **GeekJob** и **Telegram**-каналов, хранит их в **SQLite** и присылает уведомления через **Telegram-бота**.

---

## Требования

- **Python 3.11+**
- Telegram: [`API_ID` / `API_HASH`](https://my.telegram.org) (для Telethon и парсинга каналов)
- Токен бота от [@BotFather](https://t.me/BotFather)

## Быстрый старт

```bash
git clone https://github.com/<ваш-логин>/job-scraper.git
cd job-scraper

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Заполните в `.env` значения `TG_BOT_TOKEN`, `API_ID` и `API_HASH`.

```bash
python main.py
```

После запуска: вкладка **Настройки** (ID пользователя Telegram, интервал), **Источники**, **Фильтры**, при необходимости **Telegram**-каналы, затем запуск воркера на **Dashboard**.
