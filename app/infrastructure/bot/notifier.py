"""Реализация INotifier через aiogram Bot — отправка вакансий в Telegram."""

from __future__ import annotations

import asyncio

from aiogram import Bot
from loguru import logger

from app.application.interfaces.notifier import INotifier
from app.domain.entities import Job
from app.infrastructure.bot.formatters import format_job_html


class TelegramNotifier(INotifier):
    """Отправляет вакансии пользователю через Telegram Bot API."""

    def __init__(self, token: str) -> None:
        self._bot = Bot(token=token)

    async def send_jobs(self, user_id: int, jobs: list[Job]) -> int:
        sent = 0
        for job in jobs:
            try:
                html = format_job_html(job)
                await self._bot.send_message(
                    chat_id=user_id,
                    text=html,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as exc:
                logger.error("Ошибка отправки вакансии {}: {}", job.external_id, exc)

        logger.info("Отправлено {}/{} вакансий пользователю {}", sent, len(jobs), user_id)
        return sent

    @property
    def bot(self) -> Bot:
        return self._bot
