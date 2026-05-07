"""Основной use case — одна итерация сбора вакансий из всех источников."""

from __future__ import annotations

from loguru import logger

from app.application.dto.scrape_result import AggregationResult, ScrapeResult
from app.application.interfaces.notifier import INotifier
from app.application.interfaces.repositories import (
    IDailyStatsRepository,
    IJobRepository,
    ISettingsRepository,
    ISiteFilterRepository,
    ISourceRepository,
)
from app.application.interfaces.scrapers import IJobScraper
from app.application.services.deduplication_service import DeduplicationService
from app.application.services.title_query_match import title_matches_search_query
from app.domain.entities import Job, SiteFilter, SourceConfig
from app.domain.enums import SourceType


class AggregationService:
    """Оркестрирует один полный цикл: fetch → dedup → save → notify → stats."""

    def __init__(
        self,
        source_repo: ISourceRepository,
        site_filter_repo: ISiteFilterRepository,
        job_repo: IJobRepository,
        dedup_service: DeduplicationService,
        notifier: INotifier,
        settings_repo: ISettingsRepository,
        daily_stats_repo: IDailyStatsRepository,
        scrapers: dict[str, IJobScraper],
    ) -> None:
        self._source_repo = source_repo
        self._filter_repo = site_filter_repo
        self._job_repo = job_repo
        self._dedup = dedup_service
        self._notifier = notifier
        self._settings_repo = settings_repo
        self._stats_repo = daily_stats_repo
        self._scrapers = scrapers

    async def run_once(self) -> AggregationResult:
        """Выполнить одну полную итерацию по всем включённым источникам."""
        result = AggregationResult()
        settings = await self._settings_repo.get()
        enabled_sources = await self._source_repo.get_enabled()

        for source in enabled_sources:
            scrape_result = await self._process_source(source)
            result.results.append(scrape_result)

        total_new = result.total_new
        total_found = result.total_found

        if total_found > 0:
            await self._stats_repo.increment_found(total_found)

        if total_new > 0 and settings.target_user_id:
            all_new = []
            for sr in result.results:
                all_new.extend(sr.new)

            sent_count = await self._notifier.send_jobs(settings.target_user_id, all_new)
            await self._stats_repo.increment_sent(sent_count)

        logger.info(
            "Итерация завершена: найдено={}, новых={}", total_found, total_new
        )
        return result

    async def _process_source(self, source: SourceConfig) -> ScrapeResult:
        """Обработать один источник: fetch → dedup → save."""
        scrape_result = ScrapeResult(source=source.type)
        scraper = self._scrapers.get(source.type.value)

        if scraper is None:
            logger.warning("Нет скрейпера для источника {}", source.type)
            return scrape_result

        try:
            site_filter = await self._get_filter(source)
            fetched: list[Job] = []

            async for job in scraper.fetch(site_filter):
                fetched.append(job)

            before_pf = len(fetched)
            fetched = self._apply_title_post_filter(fetched, site_filter, source.type)
            if before_pf != len(fetched):
                logger.debug(
                    "{}: постфильтр по заголовку {} → {} записей",
                    source.type.value,
                    before_pf,
                    len(fetched),
                )

            scrape_result.fetched = fetched

            new_jobs = await self._dedup.filter_new(fetched)
            if new_jobs:
                await self._job_repo.bulk_insert(new_jobs)
                await self._dedup.mark_seen(new_jobs)
            scrape_result.new = new_jobs

            from datetime import datetime

            source.last_run_at = datetime.utcnow()
            await self._source_repo.update(source)

            logger.info(
                "{}: найдено={}, новых={}",
                source.type.value,
                len(fetched),
                len(new_jobs),
            )
        except Exception as exc:
            error_msg = f"{source.type.value}: {exc}"
            scrape_result.errors.append(error_msg)
            logger.error("Ошибка источника {}: {}", source.type.value, exc)

        return scrape_result

    async def _get_filter(self, source: SourceConfig) -> SiteFilter:
        """Получить фильтр для источника (или пустой дефолтный)."""
        if source.id is None:
            return SiteFilter(source_id=0)

        site_filter = await self._filter_repo.get_by_source_id(source.id)
        return site_filter or SiteFilter(source_id=source.id)

    @staticmethod
    def _apply_title_post_filter(
        jobs: list[Job], site_filter: SiteFilter, source_type: SourceType
    ) -> list[Job]:
        """Оставить только вакансии, где запрос отражён в заголовке (кроме Telegram)."""
        if source_type == SourceType.TELEGRAM:
            return jobs
        q = (site_filter.query_text or "").strip()
        if not q:
            return jobs
        return [j for j in jobs if title_matches_search_query(j.title, q)]
