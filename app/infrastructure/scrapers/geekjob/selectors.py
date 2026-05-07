"""CSS-селекторы для парсинга HTML geekjob.ru.

Текущая разметка (актуально на 2026):
  <ul id="serplist" class="collection serp-list">
    <li class="collection-item avatar">
      <div class="info"><a href="/vacancy/HASH">{city}<br><span class="salary">{salary}</span></a></div>
      <p class="vacancy-name"><a class="title" href="/vacancy/HASH">{title}</a></p>
      <p class="company-name"><a>{company}</a></p>
      <div class="info"><span class="remote-label">remote</span> ...</div>
    </li>
  </ul>
"""

from __future__ import annotations

VACANCY_CARD = "ul#serplist > li.collection-item, ul.serp-list > li.collection-item"
TITLE = "p.vacancy-name a.title, .vacancy-name a"
COMPANY = "p.company-name a, .company-name a"
SALARY = ".info .salary, span.salary"
CITY_BLOCK = ".info > a"  # содержит "{city}<br><span class='salary'>...</span>"
TAGS = ".info .remote-label, .info .relocate-label, .info span[class$='-label']"
