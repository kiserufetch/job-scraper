"""Абстракция нотификатора — отправка вакансий пользователю."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Job


class INotifier(ABC):
    """Контракт для отправки вакансий (Telegram / email / etc.)."""

    @abstractmethod
    async def send_jobs(self, user_id: int, jobs: list[Job]) -> int:
        """Отправить вакансии пользователю. Возвращает кол-во успешно отправленных."""
        ...
