"""Filters view — настройка фильтров для веб-источников."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.domain.entities import SiteFilter
from app.domain.enums import GradeLevel, SourceType
from app.presentation.gui.components.filter_form import FilterForm
from app.presentation.gui.theme import GROK_ON_SURFACE, GROK_ON_SURFACE_DIM

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container

_SITE_SOURCES = [SourceType.HH, SourceType.HABR, SourceType.GEEKJOB]


class FiltersView(ft.Column):
    """Экран настройки фильтров: формы для каждого веб-источника."""

    def __init__(self, container: Container) -> None:
        self._container = container
        super().__init__(
            controls=[
                ft.Text("Фильтры", size=28, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE),
                ft.Text(
                    "Настройте параметры поиска для каждого источника",
                    size=14,
                    color=GROK_ON_SURFACE_DIM,
                ),
                ft.Container(height=16),
                ft.Text("Загрузка…", size=14, color=GROK_ON_SURFACE_DIM),
            ],
            spacing=8,
        )

    def did_mount(self) -> None:
        if self.page:
            self.page.run_task(self._load_filters)

    async def _load_filters(self) -> None:
        forms: list[ft.Control] = [
            ft.Text("Фильтры", size=28, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE),
            ft.Text(
                "Настройте параметры поиска для каждого источника",
                size=14,
                color=GROK_ON_SURFACE_DIM,
            ),
            ft.Container(height=16),
        ]

        for src_type in _SITE_SOURCES:
            source = await self._container.source_repo.get_by_type(src_type)
            if source is None or source.id is None:
                continue

            existing = await self._container.site_filter_repo.get_by_source_id(source.id)

            form = FilterForm(
                source_name=src_type.value.upper(),
                initial_grade=existing.grade.value if existing and existing.grade else "",
                initial_stack=", ".join(existing.stack) if existing else "",
                initial_city=existing.city if existing else "",
                initial_query=existing.query_text if existing else "",
                initial_search_remote=existing.search_remote if existing else True,
                on_save=lambda grade, stack, city, query, remote, sid=source.id: (
                    self.page.run_task(
                        self._save_filter, sid, grade, stack, city, query, remote
                    )
                    if self.page
                    else None
                ),
            )
            forms.append(form)
            forms.append(ft.Container(height=12))

        self.controls = forms
        if self.page:
            self.page.update()

    async def _save_filter(
        self,
        source_id: int,
        grade: str,
        stack: str,
        city: str,
        query: str,
        search_remote: bool,
    ) -> None:
        site_filter = SiteFilter(
            source_id=source_id,
            grade=GradeLevel(grade) if grade else None,
            stack=[s.strip() for s in stack.split(",") if s.strip()],
            city=city,
            query_text=query,
            search_remote=search_remote,
        )
        await self._container.site_filter_repo.upsert(site_filter)

        if self.page:
            self.page.snack_bar = ft.SnackBar(ft.Text("Фильтр сохранён"), open=True)
            self.page.update()
