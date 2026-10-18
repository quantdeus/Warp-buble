# 🖖 QuantDeus Warp Literature Lab

Это проверяемая разведка **научной литературы по warp/FTL**, а не заявление о созданном FTL-двигателе.

## Источники

- **Google Books**: официальный публичный Books API, метаданные, ISBN и ссылка на книгу. Полный платный текст не скачиваем.
- **Google Академия**: в отчёте создаются поисковые ссылки; автоматическое извлечение результатов доступно только через разрешённый SerpApi, если пользователь добавил секрет `SERPAPI_API_KEY`. Мы не скрейпим Google Scholar напрямую.
- **Crossref**: DOI, название, авторы и дата публикации. Используется всегда как машиночитаемая альтернатива для научных статей.

## Роли

`Scout → Archivist → Analyst → Risk/Sherlock → Builder → QA`

Scout собирает библиографию. Archivist проверяет первоисточники и лицензии. Analyst извлекает реальные уравнения только после изучения текста. Risk проверяет энергетические условия, причинность, устойчивость и границы применимости. Builder воспроизводит математические модели. QA не пропускает необоснованные выводы.

## Автоматизация

`.github/workflows/warp-literature.yml` запускается на PR с этой лабораторией, при ручном запуске и, **только после принятия PR в main**, ежедневно в 06:13 UTC. Отчёт сохраняется в артефактах GitHub Actions, без коммитов, без изменений сайта и без обязательных платных вызовов.

Состав артефакта `warp-literature-research`: `research.json` (структурированные результаты с DOI и ISBN) и `REPORT.ru.md` (отчёт на русском языке). Если источники недоступны, это фиксируется как ошибка, а не подменяется выдуманными данными.

## QA-критерии

`geometry`, `eom`, `residual`, `nec`, `energy`, `curvature_tidal`, `horizon`, `causality`, `stability`, `eft`.

Изначально все имеют `UNKNOWN`: наличие публикации не означает физическую реализуемость FTL. Связано с [матрицей QuantDeus](https://github.com/quantdeus/quantdeus.github.io/blob/main/coordination/pillars/warp-evidence-gates.json).

## Тестовый запуск

```bash
python -m unittest discover -s research/warp-literature/tests -v
python research/warp-literature/scout.py --output /tmp/warp-literature
```

Источники: [Google Books API](https://developers.google.com/books/docs/v1/reference/volumes/list), [Google Scholar Help](https://scholar.google.com/intl/us/scholar/help.html), [Crossref API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [WarpFactory](https://github.com/NerdsWithAttitudes/WarpFactory).
