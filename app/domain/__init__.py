"""Domain-слой: сущности и перечисления, не зависящие от инфраструктуры."""

from app.domain.entities import (
    AppSettings,
    DailyStats,
    Job,
    SiteFilter,
    SourceConfig,
    TelegramChannel,
)
from app.domain.enums import GradeLevel, SourceType, WorkPlacement

__all__ = [
    "AppSettings",
    "DailyStats",
    "GradeLevel",
    "Job",
    "SiteFilter",
    "SourceConfig",
    "SourceType",
    "TelegramChannel",
    "WorkPlacement",
]
