"""Настройка loguru для всего приложения."""

import sys

from loguru import logger

from app.shared.constants import LOGS_DIR


def setup_logging() -> None:
    """Сконфигурировать loguru: stdout + файл с ротацией."""
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
        colorize=True,
    )

    logger.add(
        LOGS_DIR / "scraper_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    )
