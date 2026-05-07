"""HTML-форматирование вакансий для отправки в Telegram."""

from __future__ import annotations

from app.domain.entities import Job


def format_job_html(job: Job) -> str:
    """Сформировать HTML-сообщение для одной вакансии."""
    parts: list[str] = []

    parts.append(f'<b><a href="{_escape(job.url)}">{_escape(job.title)}</a></b>')

    if job.company:
        parts.append(f"🏢 {_escape(job.company)}")

    meta: list[str] = []
    if job.salary:
        meta.append(f"💰 {_escape(job.salary)}")
    if job.city:
        meta.append(f"📍 {_escape(job.city)}")
    if meta:
        parts.append(" | ".join(meta))

    if job.description:
        desc = job.description[:300]
        if len(job.description) > 300:
            desc += "…"
        parts.append(f"\n{_escape(desc)}")

    parts.append(f"<i>Источник: {job.source.value}</i>")

    return "\n".join(parts)


def _escape(text: str) -> str:
    """Экранировать спецсимволы HTML для Telegram."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
