"""Варианты написания токенов поиска (латиница / кириллица для популярных стеков).

Нужны для GeekJob и постфильтра по заголовку: вакансии часто пишут «Флаттер», а запрос — «Flutter».
"""

from __future__ import annotations

from typing import Final

import re

_TOKEN_SPLIT_RE: Final[re.Pattern[str]] = re.compile(r"[\s,;]+", re.UNICODE)

# Ключ и все значения — уже в casefold.
_CANONICAL_ALIASES_CF: Final[dict[str, tuple[str, ...]]] = {
    "flutter": ("flutter", "флаттер"),
    "флаттер": ("flutter", "флаттер"),
    "python": ("python", "питон"),
    "питон": ("python", "питон"),
    "django": ("django", "джанго"),
    "джанго": ("django", "джанго"),
    "kubernetes": ("kubernetes", "кубернетес", "кубернетис"),
    "кубернетес": ("kubernetes", "кубернетес", "кубернетис"),
    "кубернетис": ("kubernetes", "кубернетес", "кубернетис"),
}


def variants_for_token_casefold(token_cf: str) -> tuple[str, ...]:
    """Вернуть набор эквивалентных строк (casefold) для одного токена запроса."""
    if token_cf in _CANONICAL_ALIASES_CF:
        return _CANONICAL_ALIASES_CF[token_cf]
    return (token_cf,)


def haystack_matches_search_tokens(haystack: str, query: str) -> bool:
    """Проверить подстрочное совпадение всех значимых токенов запроса (с алиасами).

    Для GeekJob: серверный поиск отсутствует, совпадение ищем по полям карточки.
    """
    raw = (query or "").strip()
    if not raw:
        return True
    h = haystack.casefold()
    tokens = [x.strip() for x in _TOKEN_SPLIT_RE.split(raw) if x.strip()]
    significant = [t for t in tokens if len(t) >= 2] or tokens
    for tok in significant:
        tcf = tok.casefold()
        if not any(v in h for v in variants_for_token_casefold(tcf)):
            return False
    return True
