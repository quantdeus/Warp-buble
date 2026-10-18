#!/usr/bin/env python3
"""QuantDeus Warp Literature Lab: open bibliographic scouting, not FTL validation.

Reads public Google Books and Crossref bibliographic metadata. Optional Google
Scholar results via the SerpApi API when SERPAPI_API_KEY is explicitly configured.
Never scrape scholar.google.com or download restricted book text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BOOK_QUERIES = (
    "general relativity spacetime geometry",
    "quantum fields curved spacetime",
)
PAPER_QUERIES = (
    "Alcubierre warp drive spacetime",
    "physical warp drive positive energy",
    "quantum energy inequalities warp drive",
)
GATES = ("geometry", "eom", "residual", "nec", "energy",
         "curvature_tidal", "horizon", "causality", "stability", "eft")
UA = "QuantDeus-Warp-Literature-Lab/0.1 (https://github.com/quantdeus/Warp-buble)"
GOOD_TERMS = ("warp", "alcubierre", "spacetime", "relativity", "quantum", "energy",
              "einstein", "curvature", "causality", "gravit", "casimir")


def request_json(base: str, params: dict, timeout: int = 20) -> dict:
    url = base + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    return data


def clean(s: object, limit: int = 200) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()[:limit]


def relevant(title: str) -> bool:
    lower = title.lower()
    return any(word in lower for word in GOOD_TERMS)


def google_books(data: dict) -> list[dict]:
    output = []
    for item in data.get("items", [])[:5]:
        info = item.get("volumeInfo") or {}
        title = clean(info.get("title"))
        if not title or not relevant(title):
            continue
        ids = {i.get("type", ""): i.get("identifier", "")
               for i in info.get("industryIdentifiers", [])}
        output.append({
            "source": "Google Books",
            "title": title,
            "authors": [clean(x, 80) for x in info.get("authors", [])[:6]],
            "year": clean(info.get("publishedDate"), 20),
            "isbn": ids.get("ISBN_13") or ids.get("ISBN_10") or "",
            "url": clean(info.get("infoLink") or item.get("selfLink"), 500),
            "access": clean((item.get("accessInfo") or {}).get("viewability"), 30),
            "status": "BIBLIOGRAPHIC_ONLY",
        })
    return output


def crossref(data: dict) -> list[dict]:
    output = []
    for item in (data.get("message") or {}).get("items", [])[:8]:
        title = clean((item.get("title") or [""])[0])
        if not title or not relevant(title):
            continue
        authors = [clean(" ".join(filter(None, [a.get("given"), a.get("family")])), 80)
                   for a in (item.get("author") or [])[:6]]
        doi = clean(item.get("DOI"), 100)
        output.append({
            "source": "Crossref",
            "title": title,
            "authors": authors,
            "year": ((item.get("issued") or {}).get("date-parts") or [[None]])[0][0],
            "doi": doi,
            "url": "https://doi.org/" + doi if doi else clean(item.get("URL"), 500),
            "status": "METADATA_UNREVIEWED",
        })
    return output


def scholar_serpapi(data: dict) -> list[dict]:
    output = []
    for item in data.get("organic_results", [])[:5]:
        title = clean(item.get("title"))
        if not title or not relevant(title):
            continue
        output.append({
            "source": "Google Scholar / SerpApi",
            "title": title,
            "authors": [],
            "year": None,
            "url": clean(item.get("link"), 500),
            "status": "SEARCH_RESULT_UNVERIFIED",
        })
    return output


def dedup(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for item in items:
        key = (item.get("doi") or item.get("isbn") or item.get("title", "")).lower()
        key = re.sub(r"\W+", "", key)
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def scholar_links() -> list[dict]:
    return [
        {"query": q,
         "url": "https://scholar.google.com/scholar?" + urlencode({"q": q}),
         "mode": "reference/search-link, NOT automatic Scholar retrieval"}
        for q in PAPER_QUERIES
    ]


def collect(fetch=request_json) -> dict:
    books, papers, scholar, errors = [], [], [], []
    for q in BOOK_QUERIES:
        try:
            params = {"q": q, "printType": "books", "maxResults": 5}
            if os.getenv("GOOGLE_BOOKS_API_KEY"):
                params["key"] = os.environ["GOOGLE_BOOKS_API_KEY"]
            books.extend(google_books(fetch(
                "https://www.googleapis.com/books/v1/volumes", params)))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({"source": "Google Books", "query": q, "error": str(exc)[:150]})
    for q in PAPER_QUERIES:
        try:
            papers.extend(crossref(fetch("https://api.crossref.org/works", {
                "query.title": q, "rows": 8,
                "select": "DOI,title,author,issued,URL",
            })))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({"source": "Crossref", "query": q, "error": str(exc)[:150]})
    # Authorized provider integration only, no direct Scholar scraping.
    if os.getenv("SERPAPI_API_KEY"):
        for q in PAPER_QUERIES[:2]:
            try:
                scholar.extend(scholar_serpapi(fetch(
                    "https://serpapi.com/search.json", {
                        "engine": "google_scholar", "q": q,
                        "num": 5, "api_key": os.environ["SERPAPI_API_KEY"],
                    })))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                errors.append({"source": "Scholar/SerpApi", "query": q,
                               "error": str(exc)[:150]})
    return {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sources": {"google_books": "public volumes endpoint",
                    "google_scholar": "SerpApi if key present; otherwise links only",
                    "paper_metadata": "Crossref"},
        "books": dedup(books),
        "papers": dedup(papers),
        "scholar_results": dedup(scholar),
        "scholar_search_links": scholar_links(),
        "agent_handoff": {
            "Scout": "Gather and deduplicate publications; label provider and date.",
            "Archivist": "Verify DOI/ISBN, primary source and publication status.",
            "Analyst": "Extract equations and testable hypotheses only after reading primary text.",
            "Risk": "Check energy conditions, causality, stability, EFT and evidence quality.",
            "Builder": "Create reproducible calculations for shortlisted hypotheses.",
            "QA": "Never promote search metadata to physical FTL evidence.",
        },
        "warp_evidence_gates": {g: "UNKNOWN" for g in GATES},
        "physical_FTL_demonstrated": False,
        "errors": errors,
    }


def markdown(report: dict) -> str:
    lines = [
        "# QuantDeus — литературная разведка варп-двигателей",
        "",
        f"Сформировано (UTC): {report['generated_utc']}",
        "",
        "**Статус:** библиографическая разведка; НЕ физическое доказательство FTL.",
        "Оригинальные статьи и книги требуют отдельного чтения и проверки.",
        "",
        "## Книги — Google Books",
    ]
    for item in report["books"][:15]:
        lines.append(f"- [{item['title']}]({item['url']}) — "
                     f"{', '.join(item['authors'])}; {item['year']}; ISBN: {item['isbn'] or 'н/д'}")
    if not report["books"]:
        lines.append("- Подтверждённых результатов пока нет.")
    lines.extend(["", "## Статьи — Crossref (проверить первоисточник)"])
    for item in report["papers"][:20]:
        lines.append(f"- [{item['title']}]({item['url']}) — "
                     f"{item['year'] or 'н/д'}; DOI: {item['doi'] or 'н/д'}")
    if not report["papers"]:
        lines.append("- Подтверждённых результатов пока нет.")
    lines.extend(["", "## Google Академия — поиск и сверка"])
    for link in report["scholar_search_links"]:
        lines.append(f"- [{link['query']}]({link['url']})")
    if report["scholar_results"]:
        lines.extend(["", "### Результаты через разрешённый SerpApi (проверить вручную)"])
        for item in report["scholar_results"]:
            lines.append(f"- [{item['title']}]({item['url']})")
    lines.extend([
        "", "## Гипотезы для Analyst → Builder → Risk → QA",
        "1. Можно ли воспроизвести энергетические условия для конкретной метрики с указанием наблюдателей?",
        "2. Сохраняется ли причинность и устойчивость при требуемых скоростях?",
        "3. Совместимы ли требуемые источники материи/энергии с квантовыми ограничениями?",
        "4. Какой численный тест способен опровергнуть или уточнить модель?",
        "", "## Проверки",
        "- Все 10 научных evidence gates остаются **UNKNOWN**, пока нет проверок конкретной метрики.",
        "- **FTL не продемонстрирован.** Не заменять первоисточник автоматической аннотацией.",
    ])
    if report["errors"]:
        lines.extend(["", "## Ошибки источников"])
        for e in report["errors"]:
            lines.append(f"- {e['source']}: {e['query']} — {e['error']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="warp-literature-out")
    args = p.parse_args()
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=True)
    result = collect()
    (folder / "research.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "REPORT.ru.md").write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"books": len(result["books"]),
                      "papers": len(result["papers"]),
                      "scholar": len(result["scholar_results"]),
                      "errors": len(result["errors"]),
                      "physical_FTL_demonstrated": False}))
    return 0 if (result["books"] or result["papers"] or result["scholar_results"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
