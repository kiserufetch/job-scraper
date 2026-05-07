"""Репозиторий суточной статистики."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import IDailyStatsRepository
from app.domain.entities import DailyStats
from app.infrastructure.persistence.models import DailyStatsModel


class DailyStatsRepository(IDailyStatsRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_or_create_today(self) -> DailyStats:
        today = date.today()
        async with self._sf() as session:
            stmt = select(DailyStatsModel).where(DailyStatsModel.date == today)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                model = DailyStatsModel(date=today, found_count=0, sent_count=0)
                session.add(model)
                await session.commit()
                await session.refresh(model)

            return self._to_entity(model)

    async def increment_found(self, count: int) -> None:
        today = date.today()
        await self._ensure_today_exists()
        async with self._sf() as session:
            stmt = (
                update(DailyStatsModel)
                .where(DailyStatsModel.date == today)
                .values(found_count=DailyStatsModel.found_count + count)
            )
            await session.execute(stmt)
            await session.commit()

    async def increment_sent(self, count: int) -> None:
        today = date.today()
        await self._ensure_today_exists()
        async with self._sf() as session:
            stmt = (
                update(DailyStatsModel)
                .where(DailyStatsModel.date == today)
                .values(sent_count=DailyStatsModel.sent_count + count)
            )
            await session.execute(stmt)
            await session.commit()

    async def _ensure_today_exists(self) -> None:
        """Гарантировать наличие записи за сегодня."""
        await self.get_or_create_today()

    @staticmethod
    def _to_entity(m: DailyStatsModel) -> DailyStats:
        return DailyStats(
            id=m.id,
            date=m.date,
            found_count=m.found_count,
            sent_count=m.sent_count,
        )
