"""Воркер-обёртка над AggregationService для вызова из планировщика."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from app.application.services.aggregation_service import AggregationService


class ScraperWorker:
    """Исполняет один тик агрегации; вызывается из APScheduler."""

    def __init__(self, aggregation_service: AggregationService) -> None:
        self._service = aggregation_service
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    async def tick(self) -> None:
        """Одна итерация сбора вакансий. Защита от параллельного запуска."""
        if self._running:
            logger.debug("Воркер уже выполняется — пропуск тика")
            return

        self._running = True
        try:
            logger.info("--- Тик воркера: начало итерации ---")
            result = await self._service.run_once()
            logger.info(
                "--- Тик воркера: завершён (найдено={}, новых={}) ---",
                result.total_found,
                result.total_new,
            )
        except Exception as exc:
            logger.error("Критическая ошибка в воркере: {}", exc)
        finally:
            self._running = False
