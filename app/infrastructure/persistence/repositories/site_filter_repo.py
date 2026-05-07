"""Репозиторий фильтров для веб-источников."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import ISiteFilterRepository
from app.domain.entities import SiteFilter
from app.domain.enums import GradeLevel
from app.infrastructure.persistence.models import SiteFilterModel


class SiteFilterRepository(ISiteFilterRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_by_source_id(self, source_id: int) -> SiteFilter | None:
        async with self._sf() as session:
            stmt = select(SiteFilterModel).where(SiteFilterModel.source_id == source_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def upsert(self, site_filter: SiteFilter) -> SiteFilter:
        async with self._sf() as session:
            if site_filter.id is not None:
                model = await session.get(SiteFilterModel, site_filter.id)
            else:
                stmt = select(SiteFilterModel).where(
                    SiteFilterModel.source_id == site_filter.source_id
                )
                result = await session.execute(stmt)
                model = result.scalar_one_or_none()

            if model is None:
                model = SiteFilterModel(source_id=site_filter.source_id)
                session.add(model)

            model.grade = site_filter.grade.value if site_filter.grade else None
            model.stack = site_filter.stack
            model.city = site_filter.city
            model.query_text = site_filter.query_text
            model.search_remote = site_filter.search_remote

            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    @staticmethod
    def _to_entity(m: SiteFilterModel) -> SiteFilter:
        return SiteFilter(
            id=m.id,
            source_id=m.source_id,
            grade=GradeLevel(m.grade) if m.grade else None,
            stack=m.stack or [],
            city=m.city or "",
            query_text=m.query_text or "",
            search_remote=m.search_remote if m.search_remote is not None else True,
        )
