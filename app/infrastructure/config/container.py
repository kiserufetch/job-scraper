"""DI-контейнер — ручная сборка зависимостей без тяжёлых фреймворков."""

from __future__ import annotations

from app.application.interfaces.notifier import INotifier
from app.application.interfaces.repositories import (
    IDailyStatsRepository,
    IJobRepository,
    ISeenJobsRepository,
    ISettingsRepository,
    ISiteFilterRepository,
    ISourceRepository,
    ITelegramChannelRepository,
)
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.application.services.aggregation_service import AggregationService
from app.application.services.deduplication_service import DeduplicationService
from app.infrastructure.bot.notifier import TelegramNotifier
from app.infrastructure.config.env_settings import EnvSettings
from app.infrastructure.persistence.database import DatabaseManager
from app.infrastructure.persistence.repositories.daily_stats_repo import DailyStatsRepository
from app.infrastructure.persistence.repositories.job_repo import JobRepository
from app.infrastructure.persistence.repositories.seen_jobs_repo import SeenJobsRepository
from app.infrastructure.persistence.repositories.settings_repo import SettingsRepository
from app.infrastructure.persistence.repositories.site_filter_repo import SiteFilterRepository
from app.infrastructure.persistence.repositories.source_repo import SourceRepository
from app.infrastructure.persistence.repositories.telegram_channel_repo import (
    TelegramChannelRepository,
)
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.scrapers.habr.habr_rss_scraper import HabrRssScraper
from app.infrastructure.scrapers.hh.hh_api_scraper import HhApiScraper
from app.infrastructure.scrapers.geekjob.geekjob_scraper import GeekJobScraper
from app.infrastructure.scrapers.http.client_factory import HttpClientFactory
from app.infrastructure.scrapers.telegram.telethon_scraper import TelethonScraper


class Container:
    """Центральный контейнер зависимостей приложения.

    Инициализация ленивая: тяжёлые объекты создаются при первом доступе.
    """

    def __init__(self) -> None:
        self.env = EnvSettings()  # type: ignore[call-arg]
        self.db = DatabaseManager()

        self._http_factory: HttpClientFactory | None = None
        self._uow: SqlAlchemyUnitOfWork | None = None
        self._notifier: TelegramNotifier | None = None

    # -- Persistence -----------------------------------------------------------

    @property
    def session_factory(self):
        return self.db.session_factory

    @property
    def uow(self) -> IUnitOfWork:
        if self._uow is None:
            self._uow = SqlAlchemyUnitOfWork(self.session_factory)
        return self._uow

    @property
    def job_repo(self) -> IJobRepository:
        return JobRepository(self.session_factory)

    @property
    def seen_jobs_repo(self) -> ISeenJobsRepository:
        return SeenJobsRepository(self.session_factory)

    @property
    def source_repo(self) -> ISourceRepository:
        return SourceRepository(self.session_factory)

    @property
    def site_filter_repo(self) -> ISiteFilterRepository:
        return SiteFilterRepository(self.session_factory)

    @property
    def telegram_channel_repo(self) -> ITelegramChannelRepository:
        return TelegramChannelRepository(self.session_factory)

    @property
    def settings_repo(self) -> ISettingsRepository:
        return SettingsRepository(self.session_factory)

    @property
    def daily_stats_repo(self) -> IDailyStatsRepository:
        return DailyStatsRepository(self.session_factory)

    # -- HTTP ------------------------------------------------------------------

    @property
    def http_factory(self) -> HttpClientFactory:
        if self._http_factory is None:
            self._http_factory = HttpClientFactory()
        return self._http_factory

    # -- Scrapers --------------------------------------------------------------

    @property
    def hh_scraper(self) -> HhApiScraper:
        return HhApiScraper(self.http_factory)

    @property
    def habr_scraper(self) -> HabrRssScraper:
        return HabrRssScraper(self.http_factory)

    @property
    def geekjob_scraper(self) -> GeekJobScraper:
        return GeekJobScraper(self.http_factory)

    @property
    def telegram_scraper(self) -> TelethonScraper:
        return TelethonScraper(
            api_id=self.env.api_id,
            api_hash=self.env.api_hash,
            channel_repo=self.telegram_channel_repo,
        )

    # -- Services --------------------------------------------------------------

    @property
    def notifier(self) -> INotifier:
        if self._notifier is None:
            self._notifier = TelegramNotifier(self.env.tg_bot_token)
        return self._notifier

    @property
    def deduplication_service(self) -> DeduplicationService:
        return DeduplicationService(self.seen_jobs_repo)

    @property
    def aggregation_service(self) -> AggregationService:
        return AggregationService(
            source_repo=self.source_repo,
            site_filter_repo=self.site_filter_repo,
            job_repo=self.job_repo,
            dedup_service=self.deduplication_service,
            notifier=self.notifier,
            settings_repo=self.settings_repo,
            daily_stats_repo=self.daily_stats_repo,
            scrapers={
                "hh": self.hh_scraper,
                "habr": self.habr_scraper,
                "geekjob": self.geekjob_scraper,
                "telegram": self.telegram_scraper,
            },
        )

    # -- Lifecycle -------------------------------------------------------------

    async def init(self) -> None:
        """Инициализировать БД (создать таблицы, заполнить начальные данные)."""
        await self.db.init()

    async def close(self) -> None:
        """Освободить ресурсы при завершении."""
        if self._http_factory:
            await self._http_factory.close()
        await self.db.close()
