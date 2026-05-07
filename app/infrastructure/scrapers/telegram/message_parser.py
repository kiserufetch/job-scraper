"""Парсинг сообщений Telegram-канала в доменные Job-сущности."""

from __future__ import annotations

import re
from datetime import datetime

from app.domain.entities import Job
from app.domain.enums import SourceType

_URL_RE = re.compile(r"https?://\S+")


def message_matches_keywords(text: str, keywords: list[str]) -> bool:
    """Проверить, содержит ли текст хотя бы одно ключевое слово (регистронезависимо)."""
    if not keywords:
        return True
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def message_to_job(
    channel_id: int,
    channel_username: str,
    message_id: int,
    text: str,
    date: datetime | None,
) -> Job:
    """Преобразовать сообщение TG-канала в Job."""
    urls = _URL_RE.findall(text)
    first_url = urls[0] if urls else f"https://t.me/{channel_username}/{message_id}"

    lines = text.strip().split("\n")
    title = lines[0][:200] if lines else "Вакансия из Telegram"

    return Job(
        external_id=f"{channel_id}:{message_id}",
        source=SourceType.TELEGRAM,
        title=title,
        company=f"@{channel_username}",
        url=first_url,
        description=text[:2000],
        published_at=date,
    )
