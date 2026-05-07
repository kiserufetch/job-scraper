"""Репозиторий дедупликации (seen_jobs)."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import ISeenJobsRepository
from app.infrastructure.persistence.models import SeenJobModel


class SeenJobsRepository(ISeenJobsRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def filter_unseen(self, hashes: list[str]) -> set[str]:
        if not hashes:
            return set()

        async with self._sf() as session:
            stmt = select(SeenJobModel.hash).where(SeenJobModel.hash.in_(hashes))
            result = await session.execute(stmt)
            existing = {row[0] for row in result.all()}
            return set(hashes) - existing

    async def bulk_mark_seen(self, hashes: list[str]) -> None:
        if not hashes:
            return

        async with self._sf() as session:
            models = [SeenJobModel(hash=h) for h in hashes]
            session.add_all(models)
            await session.commit()

    async def clear_all(self) -> int:
        async with self._sf() as session:
            count_stmt = select(func.count()).select_from(SeenJobModel)
            count = (await session.execute(count_stmt)).scalar() or 0
            await session.execute(delete(SeenJobModel))
            await session.commit()
            return count
