"""Репозиторий источников вакансий."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import ISourceRepository
from app.domain.entities import SourceConfig
from app.domain.enums import SourceType
from app.infrastructure.persistence.models import SourceModel


class SourceRepository(ISourceRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_all(self) -> list[SourceConfig]:
        async with self._sf() as session:
            result = await session.execute(select(SourceModel))
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_enabled(self) -> list[SourceConfig]:
        async with self._sf() as session:
            stmt = select(SourceModel).where(SourceModel.is_enabled.is_(True))
            result = await session.execute(stmt)
            return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, source: SourceConfig) -> None:
        async with self._sf() as session:
            model = await session.get(SourceModel, source.id)
            if model is None:
                return
            model.is_enabled = source.is_enabled
            model.last_run_at = source.last_run_at
            await session.commit()

    async def get_by_type(self, source_type: SourceType) -> SourceConfig | None:
        async with self._sf() as session:
            stmt = select(SourceModel).where(SourceModel.type == source_type.value)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(m: SourceModel) -> SourceConfig:
        return SourceConfig(
            id=m.id,
            type=SourceType(m.type),
            is_enabled=m.is_enabled,
            last_run_at=m.last_run_at,
        )
