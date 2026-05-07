"""Репозиторий вакансий."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import IJobRepository
from app.domain.entities import Job
from app.domain.enums import SourceType, WorkPlacement
from app.infrastructure.persistence.models import JobModel


class JobRepository(IJobRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def bulk_insert(self, jobs: list[Job]) -> list[Job]:
        async with self._sf() as session:
            models = [
                JobModel(
                    external_id=j.external_id,
                    source=j.source.value,
                    title=j.title,
                    company=j.company,
                    salary=j.salary,
                    city=j.city,
                    url=j.url,
                    description=j.description,
                    work_placement=j.work_placement.value,
                    published_at=j.published_at,
                )
                for j in jobs
            ]
            session.add_all(models)
            await session.commit()

            for model, entity in zip(models, jobs):
                entity.id = model.id
            return jobs

    async def get_jobs_by_date(self, target_date: date) -> list[Job]:
        async with self._sf() as session:
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())

            stmt = select(JobModel).where(
                JobModel.created_at.between(start, end)
            )
            result = await session.execute(stmt)
            return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(m: JobModel) -> Job:
        wp_raw = getattr(m, "work_placement", None) or "unknown"
        try:
            wp = WorkPlacement(wp_raw)
        except ValueError:
            wp = WorkPlacement.UNKNOWN

        return Job(
            id=m.id,
            external_id=m.external_id,
            source=SourceType(m.source),
            title=m.title,
            company=m.company,
            salary=m.salary,
            city=m.city,
            url=m.url,
            description=m.description,
            work_placement=wp,
            published_at=m.published_at,
            created_at=m.created_at,
        )
