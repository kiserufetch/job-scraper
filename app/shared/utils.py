"""Общие утилиты проекта."""

import hashlib

from app.domain.enums import SourceType


def compute_job_hash(source: SourceType, external_id: str) -> str:
    """Стабильный SHA-256 хеш для дедупликации вакансий."""
    raw = f"{source.value}:{external_id}"
    return hashlib.sha256(raw.encode()).hexdigest()
