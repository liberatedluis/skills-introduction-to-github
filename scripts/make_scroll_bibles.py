#!/usr/bin/env python3
"""Write 1,300 Matrix-scrollable Holy Bible HTML pages into scroll-bibles/."""

from __future__ import annotations

import html
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import BRAND, CREDIT, SITE, SITE_URL  # noqa: E402
from copy_holy_bibles_to_desktop import coverage_label  # noqa: E402
from holy_catalog import build_catalog  # noqa: E402

OUT = ROOT / "scroll-bibles"
PAGES = "https://liberatedluis.github.io/skills-introduction-to-github"
COVERAGE = {"bible": "Full Bible", "nt": "New Testament", "portions": "Portions"}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def href(name: str) -> str:
    return quote(name, safe="")


def start_book(row: dict) -> str:
    return "gen" if row.get("coverage") == "bible" else "mat"


def head(title: str, base: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="color-scheme" content="dark" />
    <meta name="theme-color" content="#041208" />
    <base href="{esc(base)}" />
    <meta name="description" content="{esc(description)}" />
    <title>{esc(title)}</title>
    <link rel="icon" href="assets/img/mark.svg" type="image/svg+xml" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="assets/css/app.css" />
  </head>
"""


def chrome(extra_actions: str = "") -> str:
    return f"""    <canvas id="rain" aria-hidden="true"></canvas>
    <div class="scanlines" aria-hidden="true"></div>
    <header class="topbar">
      <a class="brand" href="index.html">
        <img src="assets/img/mark.svg" width="40" height="40" alt="" />
        <span>
          <strong>{esc(BRAND)}</strong>
          <em>1,300 scrollable Matrix translations · {esc(CREDIT)}</em>
          <b>{esc(SITE)}</b>
        </span>
      </a>
      <div class="top-actions">
        <span class="tx-count">1,300 translations</span>
        <button type="button" id="themeBtn" class="ghost" aria-label="Toggle color theme">Theme</button>
        {extra_actions}
        <a class="ghost site-link" href="{esc(SITE_URL)}" target="_blank" rel="noopener">{esc(SITE)}</a>
      </div>
    </header>
"""


def bible_page(row: dict) -> str:
    book = start_book(row)
    title = f"{row.get('title') or row['id']} · {BRAND}"
    desc = f"{coverage_label(row)} in {row.get('language') or row['id']} — Matrix scroller · {SITE}"
    tx = row["id"]
    native = row.get("native") or row.get("language") or tx
    language = row.get("language") or ""
    return (
        head(title, "../../../", desc)
        + f"""  <body data-tx="{esc(tx)}" data-usfm="{esc(book)}" data-chapter="1">
{chrome(
            extra_actions='<a class="ghost" href="scroll-bibles/index.html">All 1,300</a> <a class="ghost" href="print.html">1,300 print PDFs</a>'
        )}
    <form class="controls" id="controls" autocomplete="off">
      <label class="grow">
        Translation
        <input id="langSearch" type="search" placeholder="Search 1,300 Matrix Holy Bibles" enterkeyhint="search" />
      </label>
      <label>
        Book
        <select id="bookSelect"></select>
      </label>
      <label>
        Chapter
        <select id="chapterSelect"></select>
      </label>
      <fieldset class="modes">
        <legend>Format</legend>
        <label><input type="radio" name="mode" value="scroll" checked /> Scroll</label>
        <label><input type="radio" name="mode" value="txt" /> TXT</label>
        <label><input type="radio" name="mode" value="pdf" /> PDF</label>
      </fieldset>
    </form>
    <div id="langPanel" class="lang-panel" hidden></div>
    <p id="status" class="status" role="status">Loading {esc(native)} / {esc(language)} · {esc(SITE)}</p>
    <main id="stage">
      <section id="view-scroll" class="view scroll-view" data-mode="scroll"></section>
      <section id="view-txt" class="view txt-view" data-mode="txt" hidden></section>
      <section id="view-pdf" class="view pdf-view" data-mode="pdf" hidden></section>
    </main>
    <div class="dock">
      <button type="button" id="prevBtn">Prev</button>
      <button type="button" id="nextBtn">Next</button>
      <button type="button" id="downloadTxtBtn">Download TXT</button>
      <button type="button" id="printBtn">Print / Save PDF</button>
    </div>
    <footer class="foot">
      <p>Every page is marked <a href="{esc(SITE_URL)}">{esc(SITE)}</a></p>
      <p>{esc(BRAND)} · {esc(CREDIT)}</p>
    </footer>
    <script>
      if (!location.hash) {{
        history.replaceState({{}}, "", location.pathname + location.search + "#{esc(tx)}/{esc(book)}/1/scroll");
      }}
    </script>
    <script src="assets/js/app.js" type="module"></script>
  </body>
</html>
"""
    )


def list_page(title: str, base: str, lede: str, cards: str, crumb: str) -> str:
    return (
        head(title, base, f"{title} · {SITE}")
        + f"""  <body id="printCatalog">
{chrome(
            extra_actions='<a class="ghost" href="index.html">Open the scroller</a> <a class="ghost" href="print.html">1,300 print PDFs</a>'
        )}
    <main class="print-catalog">
      <p class="lede">{crumb}</p>
      <p class="lede">{lede}</p>
      <div class="print-list">
{cards}
      </div>
    </main>
    <footer class="foot">
      <p>{esc(BRAND)} · {esc(CREDIT)} · {esc(SITE)}</p>
    </footer>
    <script src="assets/js/app.js" type="module"></script>
  </body>
</html>
"""
    )


def card(href_path: str, title: str, sub: str) -> str:
    return f"""        <article class="print-card">
          <a class="print-open" href="{esc(href_path)}">{esc(title)}<small>{esc(sub)}</small></a>
        </article>"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    catalog = build_catalog()
    if OUT.exists():
        for old in OUT.rglob("*"):
            if old.is_file():
                old.unlink()
        for old in sorted((p for p in OUT.rglob("*") if p.is_dir()), reverse=True):
            old.rmdir()
    OUT.mkdir(parents=True, exist_ok=True)

    by_letter: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    bible_files = []
    for row in catalog:
        rel = Path(row["printPath"]).with_suffix(".html").as_posix()
        row["scrollPath"] = rel
        dest = OUT / rel
        write(dest, bible_page(row))
        letter, language, filename = rel.split("/", 2)
        by_letter[letter][language].append({**row, "file": filename})
        bible_files.append(rel)

    letter_cards = []
    for letter in sorted(by_letter, key=lambda item: (item != "#", item)):
        langs = by_letter[letter]
        count = sum(len(rows) for rows in langs.values())
        write(
            OUT / letter / "index.html",
            list_page(
                f"{letter} · 1,300 Matrix Holy Bibles",
                "../../",
                f"{count} scrollable Bibles in {len(langs)} language folders · {SITE}",
                "\n".join(
                    card(
                        f"scroll-bibles/{href(letter)}/{href(language)}/index.html",
                        language,
                        f"{len(rows)} translation{'s' if len(rows) != 1 else ''}",
                    )
                    for language, rows in sorted(langs.items(), key=lambda item: item[0].casefold())
                ),
                f'<a href="scroll-bibles/index.html">1,300 Matrix Holy Bibles</a> / {esc(letter)}',
            ),
        )
        for language, rows in langs.items():
            write(
                OUT / letter / language / "index.html",
                list_page(
                    f"{language} · {BRAND}",
                    "../../../",
                    f"{len(rows)} Matrix-scrollable Christ Supply Holy Bibles · {SITE}",
                    "\n".join(
                        card(
                            f"scroll-bibles/{href(letter)}/{href(language)}/{href(item['file'])}",
                            item.get("title") or item["id"],
                            f"{coverage_label(item)} · {item['id']}",
                        )
                        for item in sorted(rows, key=lambda item: (item.get("title") or item["id"]).casefold())
                    ),
                    f'<a href="scroll-bibles/index.html">1,300</a> / <a href="scroll-bibles/{href(letter)}/index.html">{esc(letter)}</a> / {esc(language)}',
                ),
            )
        letter_cards.append(
            card(
                f"scroll-bibles/{href(letter)}/index.html",
                letter,
                f"{count} Bibles · {len(langs)} languages",
            )
        )

    write(
        OUT / "index.html",
        list_page(
            f"1,300 Matrix Holy Bibles · {BRAND}",
            "../",
            f"Open any of the {len(bible_files)} scrollable Matrix translations. Live scripture loads in the reader. Every page is marked {SITE}.",
            "\n".join(letter_cards),
            f'<a href="index.html">{esc(BRAND)}</a> · <a href="{esc(PAGES)}/scroll-bibles/">{esc(PAGES)}/scroll-bibles/</a>',
        ),
    )
    write(
        OUT / "README.md",
        f"""# {BRAND} — 1,300 Matrix scrollables

Made by {CREDIT} · [{SITE}]({SITE_URL})

These are the 1,300 scrollable Matrix Holy Bibles. Browse by letter, then language.

Live on GitHub Pages:

{PAGES}/scroll-bibles/

Example: [E/English](E/English).

Each HTML file opens that translation in the Matrix scroller. Keep scrolling to load the next chapter.
""",
    )
    (OUT / "Index of 1300 scrollables.csv").write_text(
        "letter,language,coverage,title,id,file\n"
        + "\n".join(
            f"{rel.split('/', 2)[0]},{json.dumps(rel.split('/', 2)[1], ensure_ascii=False)},{COVERAGE.get(row.get('coverage') or '', 'Portions')},{json.dumps(row.get('title') or row['id'], ensure_ascii=False)},{row['id']},{rel}"
            for row, rel in zip(catalog, bible_files)
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(bible_files)} Matrix Holy Bibles in {OUT} · {SITE}")


if __name__ == "__main__":
    main()
