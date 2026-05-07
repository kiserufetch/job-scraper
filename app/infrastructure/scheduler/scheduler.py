"""APScheduler-планировщик: управление периодическими тиками воркера."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

if TYPE_CHECKING:
    from app.infrastructure.scheduler.worker import ScraperWorker

_JOB_ID = "scraper_worker_tick"


class SchedulerManager:
    """Обёртка над APScheduler для старта/остановки воркера из GUI."""

    def __init__(self, worker: ScraperWorker, interval_minutes: int = 30) -> None:
        self._worker = worker
        self._interval = interval_minutes
        self._scheduler = AsyncIOScheduler()
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def start(self, interval_minutes: int | None = None) -> None:
        """Запустить периодический тик воркера."""
        if self._is_active:
            logger.warning("Планировщик уже запущен")
            return

        minutes = interval_minutes or self._interval
        self._scheduler.add_job(
            self._worker.tick,
            trigger=IntervalTrigger(minutes=minutes),
            id=_JOB_ID,
            replace_existing=True,
            max_instances=1,
        )

        if not self._scheduler.running:
            self._scheduler.start()

        self._is_active = True
        logger.info("Планировщик запущен (интервал: {} мин)", minutes)

    def stop(self) -> None:
        """Остановить периодические тики (без остановки самого scheduler)."""
        if not self._is_active:
            return

        try:
            self._scheduler.remove_job(_JOB_ID)
        except Exception:
            pass

        self._is_active = False
        logger.info("Планировщик остановлен")

    def update_interval(self, minutes: int) -> None:
        """Обновить интервал; если активен — перезапустить с новым."""
        self._interval = minutes
        if self._is_active:
            self.stop()
            self.start(minutes)

    async def trigger_now(self) -> None:
        """Запустить тик немедленно вне расписания."""
        await self._worker.tick()

    def shutdown(self) -> None:
        """Полностью остановить APScheduler."""
        self.stop()
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
