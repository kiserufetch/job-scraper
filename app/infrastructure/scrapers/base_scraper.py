"""Базовый класс для веб-скрейперов с общей HTTP-инфраструктурой."""

from __future__ import annotations

from abc import ABC
from collections.abc import AsyncIterator

from app.application.interfaces.scrapers import IJobScraper
from app.domain.entities import Job, SiteFilter
from app.infrastructure.scrapers.http.client_factory import HttpClientFactory


class BaseWebScraper(IJobScraper, ABC):
    """Общая база для hh, habr, geekjob — инкапсулирует HTTP-клиент."""

    def __init__(self, http_factory: HttpClientFactory) -> None:
        self._http = http_factory

    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        raise NotImplementedError
