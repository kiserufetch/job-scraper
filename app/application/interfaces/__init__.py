"""Application-интерфейсы (порты) — абстракции для инфраструктуры."""

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
from app.application.interfaces.scrapers import IJobScraper
from app.application.interfaces.unit_of_work import IUnitOfWork

__all__ = [
    "IDailyStatsRepository",
    "IJobRepository",
    "IJobScraper",
    "INotifier",
    "ISeenJobsRepository",
    "ISettingsRepository",
    "ISiteFilterRepository",
    "ISourceRepository",
    "ITelegramChannelRepository",
    "IUnitOfWork",
]
