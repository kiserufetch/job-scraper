"""Entrypoint приложения: инициализация DI, БД, запуск Flet GUI."""

from __future__ import annotations

import flet as ft
from loguru import logger

from app.infrastructure.config.container import Container
from app.presentation.gui.app import JobScraperApp
from app.shared.constants import DATA_DIR, LOGS_DIR
from app.shared.logging import setup_logging


async def _init_app(container: Container) -> None:
    """Создать директории и инициализировать БД."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    await container.init()
    logger.info("База данных инициализирована: {}", container.db._engine.url)


async def main(page: ft.Page) -> None:
    """Точка входа Flet — вызывается при открытии окна."""
    setup_logging()
    logger.info("Запуск Job Scraper...")

    container = Container()
    await _init_app(container)

    app = JobScraperApp(container)
    await app.build(page)

    logger.info("GUI запущен")


if __name__ == "__main__":
    ft.run(main)
