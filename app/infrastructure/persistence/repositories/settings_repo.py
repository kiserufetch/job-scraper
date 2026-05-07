"""Репозиторий глобальных настроек приложения."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import ISettingsRepository
from app.domain.entities import AppSettings
from app.infrastructure.persistence.models import AppSettingsModel


class SettingsRepository(ISettingsRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get(self) -> AppSettings:
        async with self._sf() as session:
            model = await session.get(AppSettingsModel, 1)
            if model is None:
                model = AppSettingsModel(id=1)
                session.add(model)
                await session.commit()
                await session.refresh(model)
            return self._to_entity(model)

    async def update(self, settings: AppSettings) -> None:
        async with self._sf() as session:
            model = await session.get(AppSettingsModel, 1)
            if model is None:
                model = AppSettingsModel(id=1)
                session.add(model)

            model.target_user_id = settings.target_user_id
            model.scrape_interval_minutes = settings.scrape_interval_minutes
            model.is_worker_running = settings.is_worker_running
            await session.commit()

    @staticmethod
    def _to_entity(m: AppSettingsModel) -> AppSettings:
        return AppSettings(
            id=m.id,
            target_user_id=m.target_user_id,
            scrape_interval_minutes=m.scrape_interval_minutes,
            is_worker_running=m.is_worker_running,
        )
