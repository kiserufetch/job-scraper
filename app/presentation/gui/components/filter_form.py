"""FilterForm — форма настройки фильтров для одного источника."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.domain.enums import GradeLevel
from app.presentation.gui.theme import GROK_ON_SURFACE, GROK_SURFACE_CONTAINER


class FilterForm(ft.Container):
    """Форма фильтра: грейд, стек, город, запрос, чекбокс «искать удалёнку»."""

    def __init__(
        self,
        source_name: str,
        initial_grade: str = "",
        initial_stack: str = "",
        initial_city: str = "",
        initial_query: str = "",
        initial_search_remote: bool = True,
        on_save: Callable[[str, str, str, str, bool], None] | None = None,
    ) -> None:
        self._on_save = on_save

        self._grade_dd = ft.Dropdown(
            label="Грейд",
            value=initial_grade or None,
            options=[ft.dropdown.Option(g.value, g.value.capitalize()) for g in GradeLevel],
            width=200,
        )
        self._stack_field = ft.TextField(
            label="Стек (через запятую)",
            value=initial_stack,
            expand=True,
        )
        self._city_field = ft.TextField(
            label="Город (офис/гибрид)",
            value=initial_city,
            width=250,
        )
        self._query_field = ft.TextField(
            label="Поисковый запрос",
            value=initial_query,
            expand=True,
        )
        self._remote_cb = ft.Checkbox(
            label="Искать удалённые вакансии (по всей РФ)",
            value=initial_search_remote,
        )
        self._save_btn = ft.ElevatedButton(
            content="Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self._handle_save,
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        source_name,
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=GROK_ON_SURFACE,
                    ),
                    ft.Row([self._grade_dd, self._city_field]),
                    self._stack_field,
                    self._query_field,
                    self._remote_cb,
                    ft.Row([self._save_btn], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=12,
            ),
            bgcolor=GROK_SURFACE_CONTAINER,
            border_radius=12,
            padding=20,
        )

    def _handle_save(self, _e: ft.ControlEvent) -> None:
        if self._on_save:
            self._on_save(
                self._grade_dd.value or "",
                self._stack_field.value or "",
                self._city_field.value or "",
                self._query_field.value or "",
                bool(self._remote_cb.value),
            )
