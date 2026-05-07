"""Общие константы проекта."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "jobs.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"
