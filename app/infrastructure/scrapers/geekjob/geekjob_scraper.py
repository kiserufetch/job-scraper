"""Скрейпер вакансий с geekjob.ru через httpx + BeautifulSoup4."""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator

from bs4 import BeautifulSoup, Tag
from loguru import logger

from app.domain.entities import Job, SiteFilter
from app.domain.enums import SourceType, WorkPlacement
from app.infrastructure.scrapers.base_scraper import BaseWebScraper
from app.infrastructure.scrapers.geekjob import selectors
from app.infrastructure.scrapers.http.client_factory import HttpClientFactory
from app.infrastructure.scrapers.http.retry_policy import scraper_retry
from app.infrastructure.scrapers.http.user_agents import get_default_headers
from app.shared.query_token_aliases import haystack_matches_search_tokens

_BASE_URL = "https://geekjob.ru/vacancies"
_MAX_PAGES = 12
_ID_RE = re.compile(r"/vacancy/([a-zA-Z0-9]+)")


class GeekJobScraper(BaseWebScraper):
    """HTML-скрапинг geekjob.ru с антибот-защитой."""

    def __init__(self, http_factory: HttpClientFactory) -> None:
        super().__init__(http_factory)
        self._limiter = http_factory.rate_limiter_for("geekjob.ru", rate=0.5)

    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        seen_ids: set[str] = set()
        query = (site_filter.query_text or "").strip()

        for page in range(1, _MAX_PAGES + 1):
            html = await self._fetch_page(page)
            if html is None:
                break

            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(selectors.VACANCY_CARD)
            if not cards:
                logger.debug("GeekJob: нет карточек на странице {}", page)
                break

            for card in cards:
                job = self._parse_card(card)
                if job is None or job.external_id in seen_ids:
                    continue
                if query and not self._matches_query(job, query):
                    continue
                seen_ids.add(job.external_id)
                yield job

            await asyncio.sleep(1.5)

    @staticmethod
    def _matches_query(job: Job, query: str) -> bool:
        """GeekJob не умеет server-side поиск — фильтруем локально (название, компания, теги)."""
        haystack = f"{job.title} {job.company} {job.description}"
        return haystack_matches_search_tokens(haystack, query)

    @scraper_retry
    async def _fetch_page(self, page: int) -> str | None:
        await self._limiter.acquire()

        params: dict[str, str | int] = {}
        if page > 1:
            params["page"] = page

        resp = await self._http.client.get(
            _BASE_URL,
            params=params,
            headers=get_default_headers(),
        )
        if resp.status_code != 200:
            logger.warning("GeekJob вернул {}", resp.status_code)
            return None
        return resp.text

    @staticmethod
    def _parse_card(card: Tag) -> Job | None:
        try:
            title_el = card.select_one(selectors.TITLE)
            if title_el is None:
                return None

            title = title_el.get_text(strip=True)
            href = str(title_el.get("href", ""))
            url = f"https://geekjob.ru{href}" if href.startswith("/") else href

            match = _ID_RE.search(href)
            if not match:
                return None
            external_id = match.group(1)

            company_el = card.select_one(selectors.COMPANY)
            company = company_el.get_text(strip=True) if company_el else ""

            salary_el = card.select_one(selectors.SALARY)
            salary = salary_el.get_text(strip=True) if salary_el else ""

            # Город лежит в .info > a как текст до <br><span class="salary">
            # Вытаскиваем текст без вложенных тегов.
            city = ""
            city_block = card.select_one(selectors.CITY_BLOCK)
            if city_block is not None:
                # Берём только прямые текстовые ноды до salary
                texts: list[str] = []
                for child in city_block.children:
                    if isinstance(child, Tag) and child.name in ("span", "br"):
                        break
                    if isinstance(child, str):
                        cleaned = child.strip()
                        if cleaned:
                            texts.append(cleaned)
                city = " ".join(texts)

            tags = [t.get_text(strip=True) for t in card.select(selectors.TAGS)]
            description = ", ".join(tags) if tags else ""

            tags_blob = " ".join(tags).casefold()
            work_placement = (
                WorkPlacement.REMOTE if "remote" in tags_blob else WorkPlacement.UNKNOWN
            )

            return Job(
                external_id=external_id,
                source=SourceType.GEEKJOB,
                title=title,
                company=company,
                salary=salary,
                city=city,
                url=url,
                description=description,
                work_placement=work_placement,
            )
        except Exception as exc:
            logger.warning("GeekJob: ошибка парсинга карточки: {}", exc)
            return None
