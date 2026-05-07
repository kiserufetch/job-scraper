"""Скрейпер вакансий hh.ru через HTML-страницу поиска.

Публичный API hh.ru закрыт с 15.12.2025 (любые запросы возвращают 403),
поэтому парсим HTML страницы /search/vacancy. data-qa атрибуты стабильные,
их используют сами разработчики hh.ru для Selenium-тестов.

Логика фильтрации:
  1) Офис/гибрид в указанном городе  (schedule=fullDay)
  2) Удалёнка по всей РФ              (schedule=remote, без area)
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator
from typing import Any

from bs4 import BeautifulSoup, Tag
from loguru import logger

from app.domain.entities import Job, SiteFilter
from app.domain.enums import SourceType
from app.infrastructure.scrapers.base_scraper import BaseWebScraper
from app.infrastructure.scrapers.hh import selectors
from app.infrastructure.scrapers.hh.mappers import HH_EXPERIENCE_MAP
from app.infrastructure.scrapers.http.client_factory import HttpClientFactory
from app.infrastructure.scrapers.http.retry_policy import scraper_retry
from app.infrastructure.scrapers.http.user_agents import get_default_headers

_BASE_URL = "https://hh.ru/search/vacancy"
_PER_PAGE = 50
_MAX_PAGES = 3
_VACANCY_ID_RE = re.compile(r"/vacancy/(\d+)")


class HhApiScraper(BaseWebScraper):
    """HTML-скрапер hh.ru. Имя класса оставлено для обратной совместимости с DI."""

    def __init__(self, http_factory: HttpClientFactory) -> None:
        super().__init__(http_factory)
        self._limiter = http_factory.rate_limiter_for("hh.ru", rate=0.5)

    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        seen_ids: set[str] = set()

        if site_filter.city:
            async for job in self._fetch_query(self._build_office_params(site_filter), seen_ids):
                yield job

        if site_filter.search_remote:
            async for job in self._fetch_query(self._build_remote_params(site_filter), seen_ids):
                yield job

    async def _fetch_query(
        self, params: dict[str, Any], seen_ids: set[str]
    ) -> AsyncIterator[Job]:
        for page in range(_MAX_PAGES):
            params["page"] = page
            html = await self._fetch_page(params)
            if html is None:
                break

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(selectors.VACANCY_CARD)
            if not cards:
                logger.debug("hh.ru: пусто на странице {} (params={})", page, params)
                break

            for card in cards:
                job = self._parse_card(card)
                if job is None or job.external_id in seen_ids:
                    continue
                seen_ids.add(job.external_id)
                yield job

            await asyncio.sleep(1.2)

    @scraper_retry
    async def _fetch_page(self, params: dict[str, Any]) -> str | None:
        await self._limiter.acquire()
        resp = await self._http.client.get(
            _BASE_URL,
            params=params,
            headers=get_default_headers(),
        )
        if resp.status_code != 200:
            logger.warning("hh.ru вернул {}: {}", resp.status_code, resp.text[:200])
            return None
        return resp.text

    @staticmethod
    def _build_office_params(f: SiteFilter) -> dict[str, Any]:
        """Офис/гибрид в указанном городе (city — это ID региона hh.ru, например 1=Москва)."""
        params: dict[str, Any] = {
            "items_on_page": _PER_PAGE,
            "schedule": "fullDay",
        }
        if f.query_text:
            params["text"] = f.query_text
        if f.city:
            params["area"] = f.city
        if f.grade and f.grade in HH_EXPERIENCE_MAP:
            params["experience"] = HH_EXPERIENCE_MAP[f.grade]
        return params

    @staticmethod
    def _build_remote_params(f: SiteFilter) -> dict[str, Any]:
        """Удалёнка по всей РФ (без area)."""
        params: dict[str, Any] = {
            "items_on_page": _PER_PAGE,
            "schedule": "remote",
        }
        if f.query_text:
            params["text"] = f.query_text
        if f.grade and f.grade in HH_EXPERIENCE_MAP:
            params["experience"] = HH_EXPERIENCE_MAP[f.grade]
        return params

    @staticmethod
    def _parse_card(card: Tag) -> Job | None:
        try:
            title_el = card.select_one(selectors.TITLE)
            if title_el is None:
                return None

            title = title_el.get_text(strip=True)
            href = str(title_el.get("href", ""))
            url = href.split("?")[0] if href else ""

            match = _VACANCY_ID_RE.search(href)
            if not match:
                return None
            external_id = match.group(1)

            company_el = card.select_one(selectors.COMPANY)
            company = company_el.get_text(strip=True) if company_el else ""

            salary_el = card.select_one(selectors.SALARY)
            salary = salary_el.get_text(" ", strip=True) if salary_el else ""

            address_el = card.select_one(selectors.ADDRESS)
            city = address_el.get_text(strip=True) if address_el else ""

            req_el = card.select_one(selectors.SNIPPET_REQUIREMENT)
            resp_el = card.select_one(selectors.SNIPPET_RESPONSIBILITY)
            description_parts = [
                el.get_text(" ", strip=True) for el in (req_el, resp_el) if el is not None
            ]
            description = " ".join(description_parts)

            return Job(
                external_id=external_id,
                source=SourceType.HH,
                title=title,
                company=company,
                salary=salary,
                city=city,
                url=url,
                description=description,
            )
        except Exception as exc:
            logger.warning("hh.ru: ошибка парсинга карточки: {}", exc)
            return None
