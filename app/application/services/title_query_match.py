"""Сопоставление поискового запроса с заголовком вакансии (постфильтр).

Используется после выдачи hh/habr/geekjob: сайты часто матчат текст запроса по описанию,
из‑за чего в результаты попадают нерелевантные карточки. Ограничение по заголовку
снимает большую часть такого шума.

Токены со «спецсимволами» (C++, .NET, node.js) ищем подстрокой — иначе границы слов ломаются.
Обычные слова (латиница/кириллица/цифры) — через границы \\b-подобные (?<!\\w)(?!\\w),
чтобы не цеплять FlutterFlow при запросе «Flutter» и не терять «Flutter-разработчик»:
дефис внутри токена переводит токен в режим подстрочного поиска.
"""

from __future__ import annotations

import re
from typing import Final

_TOKEN_SPLIT_RE: Final[re.Pattern[str]] = re.compile(r"[\s,;]+", re.UNICODE)


def title_matches_search_query(title: str, query: str) -> bool:
    """Проверить, что все значимые части запроса присутствуют в заголовке."""
    raw = (query or "").strip()
    if not raw:
        return True

    t = (title or "").strip()
    if not t:
        return False

    tokens = [x.strip() for x in _TOKEN_SPLIT_RE.split(raw) if x.strip()]
    if not tokens:
        return True

    # Односимвольные токены отбрасываем только если рядом есть более длинные (напр. «мидл flutter»).
    significant = [tok for tok in tokens if len(tok) >= 2]
    if not significant:
        significant = tokens

    title_cf = t.casefold()
    return all(_token_in_title(title_cf, tok.casefold()) for tok in significant)


def _token_in_title(title_cf: str, token_cf: str) -> bool:
    """Один токен запроса должен найтись в заголовке (casefold уже применён к обоим)."""
    if not token_cf:
        return True

    # Спецсимволы типичны для стеков; границы слов здесь дают ложные отрицания.
    if _needs_substring_match(token_cf):
        return token_cf in title_cf

    pattern = r"(?<!\w)" + re.escape(token_cf) + r"(?!\w)"
    return re.search(pattern, title_cf, re.UNICODE) is not None


def _needs_substring_match(token_cf: str) -> bool:
    if "-" in token_cf or "." in token_cf or "+" in token_cf or "#" in token_cf or "/" in token_cf:
        return True
    if any(not (ch.isalnum() or ch == "_") for ch in token_cf):
        return True
    return False
