"""Доменные сущности — чистые data-классы без зависимостей от инфраструктуры."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.enums import GradeLevel, SourceType


@dataclass
class Job:
    """Вакансия, собранная из любого источника."""

    external_id: str
    source: SourceType
    title: str
    company: str
    url: str
    salary: str = ""
    city: str = ""
    description: str = ""
    published_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: int | None = None


@dataclass
class SourceConfig:
    """Конфигурация одного источника (hh / habr / geekjob / telegram)."""

    type: SourceType
    is_enabled: bool = True
    last_run_at: datetime | None = None
    id: int | None = None


@dataclass
class SiteFilter:
    """Фильтры поиска для конкретного веб-источника."""

    source_id: int
    query_text: str = ""
    grade: GradeLevel | None = None
    stack: list[str] = field(default_factory=list)
    city: str = ""
    search_remote: bool = True
    id: int | None = None


@dataclass
class TelegramChannel:
    """Конфигурация одного Telegram-канала для парсинга."""

    channel_username: str
    is_enabled: bool = True
    keywords: list[str] = field(default_factory=list)
    id: int | None = None


@dataclass
class AppSettings:
    """Глобальные настройки приложения (single-row в БД)."""

    target_user_id: int | None = None
    scrape_interval_minutes: int = 30
    is_worker_running: bool = False
    id: int = 1


@dataclass
class DailyStats:
    """Суточная статистика по вакансиям."""

    date: date
    found_count: int = 0
    sent_count: int = 0
    id: int | None = None
