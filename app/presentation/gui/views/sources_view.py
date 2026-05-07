"""Sources view — переключатели источников."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.domain.enums import SourceType
from app.presentation.gui.components.source_switch_card import SourceSwitchCard
from app.presentation.gui.theme import GROK_ON_SURFACE, GROK_ON_SURFACE_DIM

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container

_SOURCE_LABELS: dict[str, tuple[str, str]] = {
    SourceType.HH: ("HeadHunter (hh.ru)", "Официальный API — JSON, нативные фильтры"),
    SourceType.HABR: ("Habr Career", "RSS-фид — без HTML-парсинга"),
    SourceType.GEEKJOB: ("GeekJob", "HTML-скрапинг — httpx + BS4"),
    SourceType.TELEGRAM: ("Telegram-каналы", "Telethon — парсинг по ключевым словам"),
}


class SourcesView(ft.Column):
    """Экран управления источниками: Switch on/off для каждого."""

    def __init__(self, container: Container) -> None:
        self._container = container
        self._cards: dict[str, SourceSwitchCard] = {}

        super().__init__(
            controls=[
                ft.Text("Источники", size=28, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE),
                ft.Text(
                    "Включайте и отключайте источники вакансий",
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
            self.page.run_task(self._load_sources)

    async def _load_sources(self) -> None:
        sources = await self._container.source_repo.get_all()
        cards_col: list[ft.Control] = []

        for src in sources:
            label = _SOURCE_LABELS.get(src.type, (src.type.value, ""))
            card = SourceSwitchCard(
                title=label[0],
                subtitle=label[1],
                is_enabled=src.is_enabled,
                on_toggle=lambda val, s=src: self.page.run_task(self._toggle_source, s, val)
                if self.page
                else None,
            )
            self._cards[src.type.value] = card
            cards_col.append(card)

        self.controls = [
            ft.Text("Источники", size=28, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE),
            ft.Text(
                "Включайте и отключайте источники вакансий",
                size=14,
                color=GROK_ON_SURFACE_DIM,
            ),
            ft.Container(height=16),
            *cards_col,
        ]
        if self.page:
            self.page.update()

    async def _toggle_source(self, source, enabled: bool) -> None:
        source.is_enabled = enabled
        await self._container.source_repo.update(source)
