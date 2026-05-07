# Job Scraper

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Desktop job aggregator with a **Flet** control panel. Pulls listings from **hh.ru**, **Habr Career**, **GeekJob**, and **Telegram** channels, stores them in **SQLite**, and notifies you via a **Telegram bot**.

---

## Requirements

- **Python 3.11+**
- Telegram: [`API_ID` / `API_HASH`](https://my.telegram.org) (channel scraping via Telethon)
- Bot token from [@BotFather](https://t.me/BotFather)

## Get started

```bash
git clone https://github.com/<your-username>/job-scraper.git
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

Edit `.env` and set `TG_BOT_TOKEN`, `API_ID`, and `API_HASH`.

```bash
python main.py
```

After launch: open **Settings** (bot target user ID, interval), enable **Sources**, tune **Filters**, add **Telegram** channels if needed, then start the worker from **Dashboard**.
