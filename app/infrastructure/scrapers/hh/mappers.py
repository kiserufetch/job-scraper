"""Маппинг JSON-ответа api.hh.ru в доменную сущность Job."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.entities import Job
from app.domain.enums import GradeLevel, SourceType

HH_EXPERIENCE_MAP: dict[GradeLevel, str] = {
    GradeLevel.INTERN: "noExperience",
    GradeLevel.JUNIOR: "between1And3",
    GradeLevel.MIDDLE: "between3And6",
    GradeLevel.SENIOR: "moreThan6",
}


def parse_salary(salary_data: dict[str, Any] | None) -> str:
    """Преобразовать блок salary из JSON hh.ru в строку."""
    if not salary_data:
        return ""
    parts: list[str] = []
    if salary_data.get("from"):
        parts.append(f"от {salary_data['from']}")
    if salary_data.get("to"):
        parts.append(f"до {salary_data['to']}")
    currency = salary_data.get("currency", "")
    return " ".join(parts) + (f" {currency}" if currency else "")


def vacancy_to_job(item: dict[str, Any]) -> Job:
    """Преобразовать один элемент из items[] ответа /vacancies в Job."""
    published = None
    if pub_str := item.get("published_at"):
        try:
            published = datetime.fromisoformat(pub_str)
        except (ValueError, TypeError):
            pass

    area = item.get("area", {})
    city = area.get("name", "") if isinstance(area, dict) else ""

    employer = item.get("employer", {})
    company = employer.get("name", "") if isinstance(employer, dict) else ""

    return Job(
        external_id=str(item["id"]),
        source=SourceType.HH,
        title=item.get("name", ""),
        company=company,
        salary=parse_salary(item.get("salary")),
        city=city,
        url=item.get("alternate_url", ""),
        description=item.get("snippet", {}).get("requirement", "") or "",
        published_at=published,
    )
