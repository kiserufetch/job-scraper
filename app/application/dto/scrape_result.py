"""DTO для результатов одной итерации скрапинга."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Job
from app.domain.enums import SourceType


@dataclass
class ScrapeResult:
    """Результат парсинга одного источника за один тик."""

    source: SourceType
    fetched: list[Job] = field(default_factory=list)
    new: list[Job] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def duplicates_count(self) -> int:
        return len(self.fetched) - len(self.new)


@dataclass
class AggregationResult:
    """Сводный результат итерации по всем источникам."""

    results: list[ScrapeResult] = field(default_factory=list)

    @property
    def total_found(self) -> int:
        return sum(r.fetched.__len__() for r in self.results)

    @property
    def total_new(self) -> int:
        return sum(r.new.__len__() for r in self.results)

    @property
    def total_sent(self) -> int:
        return self.total_new
