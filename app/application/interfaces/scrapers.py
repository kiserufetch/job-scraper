"""Абстракция скрейпера вакансий."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.domain.entities import Job, SiteFilter


class IJobScraper(ABC):
    """Контракт для любого источника вакансий (hh, habr, geekjob, telegram)."""

    @abstractmethod
    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        """Получить вакансии из источника по заданным фильтрам."""
        ...
