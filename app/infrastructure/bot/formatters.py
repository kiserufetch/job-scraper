"""HTML-форматирование вакансий для отправки в Telegram."""

from __future__ import annotations

from app.domain.entities import Job
from app.domain.enums import WorkPlacement

_DESCRIPTION_MAX = 200

_PLACEMENT_BRACKET_RU: dict[WorkPlacement, str] = {
    WorkPlacement.UNKNOWN: "Неизвестно",
    WorkPlacement.OFFICE: "ОФИС",
    WorkPlacement.HYBRID: "ГИБРИД",
    WorkPlacement.REMOTE: "УДАЛЁНКА",
}


def format_job_html(job: Job) -> str:
    """Сформировать HTML-сообщение для одной вакансии (parse_mode=HTML)."""
    title_show = _nz_plain(job.title)
    url = (job.url or "").strip() or "https://hh.ru"

    lines: list[str] = []
    lines.append(f'<a href="{_escape_attr(url)}">{_escape(title_show)}</a>')
    lines.append(f"💼 {_escape(_nz_plain(job.company))}")
    lines.append(f"📍 {_escape(_nz_plain(job.city))}")
    lines.append(f"💰 {_escape(_nz_plain(job.salary))}")
    lines.append("")

    bracket = _PLACEMENT_BRACKET_RU.get(job.work_placement, _PLACEMENT_BRACKET_RU[WorkPlacement.UNKNOWN])
    lines.append(f"<b>[{_escape(bracket)}]</b>")
    lines.append("")

    desc_raw = (job.description or "").strip()
    if not desc_raw:
        desc_trim = "Неизвестно"
    else:
        desc_trim = desc_raw[:_DESCRIPTION_MAX]
        if len(desc_raw) > _DESCRIPTION_MAX:
            desc_trim += "…"

    lines.append("<b>ОПИСАНИЕ:</b>")
    lines.append(f"<pre>{_escape_pre(desc_trim)}</pre>")
    lines.append("")

    lines.append(f"<b>Источник:</b> {_escape(job.source.value)}")

    return "\n".join(lines)


def _nz_plain(value: str) -> str:
    """Текст для отображения; пустое → «Неизвестно»."""
    s = (value or "").strip()
    return s if s else "Неизвестно"


def _escape(text: str) -> str:
    """Экранирование для обычного HTML-текста в Telegram."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _escape_attr(url: str) -> str:
    """Экранирование URL внутри href (достаточно & и кавычек)."""
    return url.replace("&", "&amp;").replace('"', "&quot;")


def _escape_pre(text: str) -> str:
    """Экранирование содержимого тега <pre>."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
