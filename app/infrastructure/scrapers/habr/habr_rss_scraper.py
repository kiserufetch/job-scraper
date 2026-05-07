"""Скрейпер Habr Career через RSS-фид."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
from loguru import logger

from app.domain.entities import Job, SiteFilter
from app.domain.enums import SourceType
from app.infrastructure.scrapers.base_scraper import BaseWebScraper
from app.infrastructure.scrapers.habr.description_parser import (
    extract_city,
    extract_salary,
)
from app.infrastructure.scrapers.http.client_factory import HttpClientFactory
from app.infrastructure.scrapers.http.retry_policy import scraper_retry

_RSS_URL = "https://career.habr.com/vacancies/rss"
_MAX_PAGES = 3
_PER_PAGE = 25


class HabrRssScraper(BaseWebScraper):
    """Парсит RSS-фид career.habr.com — без HTML-скрапинга."""

    def __init__(self, http_factory: HttpClientFactory) -> None:
        super().__init__(http_factory)
        self._limiter = http_factory.rate_limiter_for("career.habr.com", rate=1.0)

    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        for page in range(1, _MAX_PAGES + 1):
            feed_text = await self._fetch_rss_page(site_filter.query_text, page)
            if feed_text is None:
                break

            feed = feedparser.parse(feed_text)
            entries = feed.get("entries", [])
            if not entries:
                break

            for entry in entries:
                job = self._parse_entry(entry, site_filter)
                if job is not None:
                    yield job

    @scraper_retry
    async def _fetch_rss_page(self, query: str, page: int) -> str | None:
        await self._limiter.acquire()
        params = {"page": page, "per_page": _PER_PAGE}
        if query:
            params["q"] = query

        resp = await self._http.client.get(_RSS_URL, params=params)
        if resp.status_code != 200:
            logger.warning("Habr RSS вернул {}", resp.status_code)
            return None
        return resp.text

    def _parse_entry(self, entry: dict, _site_filter: SiteFilter) -> Job | None:
        try:
            desc = entry.get("summary", "") or entry.get("description", "")

            published = self._parse_date(entry.get("published"))

            return Job(
                external_id=str(entry.get("id", entry.get("link", ""))),
                source=SourceType.HABR,
                title=entry.get("title", ""),
                company=entry.get("author", ""),
                salary=extract_salary(desc),
                city=extract_city(desc),
                url=entry.get("link", ""),
                description=desc,
                published_at=published,
            )
        except Exception as exc:
            logger.warning("Habr: ошибка парсинга entry: {}", exc)
            return None

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            return None
