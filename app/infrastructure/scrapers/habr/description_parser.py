"""Парсинг description из RSS Habr Career — извлечение грейда, стека, города."""

from __future__ import annotations

import re

from app.domain.enums import GradeLevel

_GRADE_PATTERNS: dict[GradeLevel, re.Pattern[str]] = {
    GradeLevel.INTERN: re.compile(r"#intern", re.IGNORECASE),
    GradeLevel.JUNIOR: re.compile(r"#junior", re.IGNORECASE),
    GradeLevel.MIDDLE: re.compile(r"#middle", re.IGNORECASE),
    GradeLevel.SENIOR: re.compile(r"#senior", re.IGNORECASE),
    GradeLevel.LEAD: re.compile(r"#lead", re.IGNORECASE),
}

_TAG_RE = re.compile(r"#(\S+)")
_CITY_RE = re.compile(r"([А-ЯЁ][а-яё\-]+(?:\s[А-ЯЁ][а-яё\-]+)?)\s*\(Россия\)")
_SALARY_RE = re.compile(r"(?:от|до|От|До)\s[\d\s]+[₽$€]", re.UNICODE)


def extract_grade(desc: str) -> GradeLevel | None:
    """Извлечь грейд из #-тегов описания."""
    for grade, pattern in _GRADE_PATTERNS.items():
        if pattern.search(desc):
            return grade
    return None


def extract_tags(desc: str) -> list[str]:
    """Извлечь все #-теги как список строк."""
    return _TAG_RE.findall(desc)


def extract_city(desc: str) -> str:
    """Попытаться извлечь город из текста описания."""
    match = _CITY_RE.search(desc)
    return match.group(1) if match else ""


def extract_salary(desc: str) -> str:
    """Извлечь информацию о зарплате из описания."""
    parts = _SALARY_RE.findall(desc)
    return " ".join(parts).strip() if parts else ""
