"""Абстракции репозиториев для работы с данными."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities import (
    AppSettings,
    DailyStats,
    Job,
    SiteFilter,
    SourceConfig,
    TelegramChannel,
)
from app.domain.enums import SourceType


class IJobRepository(ABC):
    """Работа с вакансиями в БД."""

    @abstractmethod
    async def bulk_insert(self, jobs: list[Job]) -> list[Job]:
        ...

    @abstractmethod
    async def get_jobs_by_date(self, target_date: date) -> list[Job]:
        ...


class ISeenJobsRepository(ABC):
    """Проверка и запись уже отправленных вакансий (дедупликация)."""

    @abstractmethod
    async def filter_unseen(self, hashes: list[str]) -> set[str]:
        """Вернуть подмножество хешей, которых ещё нет в seen_jobs."""
        ...

    @abstractmethod
    async def bulk_mark_seen(self, hashes: list[str]) -> None:
        ...

    @abstractmethod
    async def clear_all(self) -> int:
        """Удалить все записи. Возвращает количество удалённых строк."""
        ...


class ISourceRepository(ABC):
    """Управление источниками."""

    @abstractmethod
    async def get_all(self) -> list[SourceConfig]:
        ...

    @abstractmethod
    async def get_enabled(self) -> list[SourceConfig]:
        ...

    @abstractmethod
    async def update(self, source: SourceConfig) -> None:
        ...

    @abstractmethod
    async def get_by_type(self, source_type: SourceType) -> SourceConfig | None:
        ...


class ISiteFilterRepository(ABC):
    """Управление фильтрами для веб-источников."""

    @abstractmethod
    async def get_by_source_id(self, source_id: int) -> SiteFilter | None:
        ...

    @abstractmethod
    async def upsert(self, site_filter: SiteFilter) -> SiteFilter:
        ...


class ITelegramChannelRepository(ABC):
    """Управление Telegram-каналами."""

    @abstractmethod
    async def get_all(self) -> list[TelegramChannel]:
        ...

    @abstractmethod
    async def get_enabled(self) -> list[TelegramChannel]:
        ...

    @abstractmethod
    async def add(self, channel: TelegramChannel) -> TelegramChannel:
        ...

    @abstractmethod
    async def update(self, channel: TelegramChannel) -> None:
        ...

    @abstractmethod
    async def delete(self, channel_id: int) -> None:
        ...


class ISettingsRepository(ABC):
    """Глобальные настройки приложения."""

    @abstractmethod
    async def get(self) -> AppSettings:
        ...

    @abstractmethod
    async def update(self, settings: AppSettings) -> None:
        ...


class IDailyStatsRepository(ABC):
    """Суточная статистика."""

    @abstractmethod
    async def get_or_create_today(self) -> DailyStats:
        ...

    @abstractmethod
    async def increment_found(self, count: int) -> None:
        ...

    @abstractmethod
    async def increment_sent(self, count: int) -> None:
        ...
