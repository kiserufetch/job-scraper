"""Нормализация поля «город» в идентификатор региона hh.ru для параметра area.

Пользователь может ввести «Санкт-Петербург» или «2». Чистое число передаём как есть.
Иначе ищем по карте синонимов — иначе hh может игнорировать фильтр или подставить неверный регион.

Для удалённых вакансий используется area=113 (Россия), чтобы не тащить офисные вакансии из других стран
в общую выдачу при смешанных режимах поиска на стороне hh.
"""

from __future__ import annotations

import re
from typing import Final

_HH_RUSSIA_AREA_ID: Final[str] = "113"

_NAME_TO_AREA: Final[dict[str, str]] = {
    "москва": "1",
    "moscow": "1",
    "мск": "1",
    "санкт-петербург": "2",
    "санктпетербург": "2",
    "санкт петербург": "2",
    "спб": "2",
    "питер": "2",
    "питербург": "2",
    "saint petersburg": "2",
    "st petersburg": "2",
    "stpetersburg": "2",
    "новосибирск": "4",
    "екатеринбург": "3",
    "нижний новгород": "66",
    "нижнийновгород": "66",
    "казань": "88",
    "краснодар": "1438",
    "самара": "78",
    "уфа": "99",
}


def normalize_hh_area_id(city_raw: str) -> str | None:
    """Вернуть строковый ID региона для URL hh.ru или None, если область задать нельзя."""
    s = (city_raw or "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d+", s):
        return s
    key = s.casefold().replace("ё", "е")
    for ch in "-_:":
        key = key.replace(ch, " ")
    key = " ".join(key.split())
    aid = _NAME_TO_AREA.get(key)
    return aid if aid else None


def hh_remote_area_param() -> tuple[str, str]:
    """Параметр area для поиска удалёнки в пределах России."""
    return ("area", _HH_RUSSIA_AREA_ID)
