"""Сервис дедупликации вакансий через seen_jobs."""

from __future__ import annotations

from app.application.interfaces.repositories import ISeenJobsRepository
from app.domain.entities import Job
from app.shared.utils import compute_job_hash


class DeduplicationService:
    """Фильтрует уже отправленные вакансии и помечает новые как seen."""

    def __init__(self, seen_repo: ISeenJobsRepository) -> None:
        self._seen_repo = seen_repo

    async def filter_new(self, jobs: list[Job]) -> list[Job]:
        """Вернуть только те вакансии, которых ещё нет в seen_jobs."""
        if not jobs:
            return []

        hash_map = {compute_job_hash(j.source, j.external_id): j for j in jobs}
        unseen_hashes = await self._seen_repo.filter_unseen(list(hash_map.keys()))
        return [hash_map[h] for h in unseen_hashes]

    async def mark_seen(self, jobs: list[Job]) -> None:
        """Пометить вакансии как отправленные."""
        if not jobs:
            return
        hashes = [compute_job_hash(j.source, j.external_id) for j in jobs]
        await self._seen_repo.bulk_mark_seen(hashes)
