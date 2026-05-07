"""ViewModel для Dashboard — управление воркером."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container

_scheduler_instance = None


class DashboardViewModel:
    """Управляет планировщиком и запросом статистики."""

    def __init__(self, container: Container) -> None:
        self._container = container

    def _get_scheduler(self):
        global _scheduler_instance
        if _scheduler_instance is None:
            from app.infrastructure.scheduler.scheduler import SchedulerManager
            from app.infrastructure.scheduler.worker import ScraperWorker

            worker = ScraperWorker(self._container.aggregation_service)
            _scheduler_instance = SchedulerManager(worker)
        return _scheduler_instance

    async def start_worker(self) -> None:
        settings = await self._container.settings_repo.get()
        scheduler = self._get_scheduler()
        scheduler.start(settings.scrape_interval_minutes)

        settings.is_worker_running = True
        await self._container.settings_repo.update(settings)

    async def stop_worker(self) -> None:
        scheduler = self._get_scheduler()
        scheduler.stop()

        settings = await self._container.settings_repo.get()
        settings.is_worker_running = False
        await self._container.settings_repo.update(settings)

    async def run_now(self) -> None:
        scheduler = self._get_scheduler()
        await scheduler.trigger_now()
