#!/usr/bin/env python3
"""Build print-friendly Christ Supply Holy Bible PDFs with ChristSupply.Net on every page."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
SITE = "ChristSupply.Net"
BRAND = "Christ Supply Holy Bible"
CREDIT = "Made by Liberated Luis With Cursor, Claude Opus, and MacBook"

UA = {"User-Agent": "ChristSupplyBible/1.0"}


def get_json(url: str):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def strip_markup(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_verses(iso: str, book_id: int, chapter: int) -> tuple[dict, dict, list[dict]]:
    lang = next(row for row in CATALOG["languages"] if row["iso"] == iso)
    book = next(row for row in BOOKS if row["id"] == book_id)
    errors = []
    for source in lang.get("sources") or []:
        try:
            if source["kind"] == "bolls":
                rows = get_json(f"https://bolls.life/get-text/{source['id']}/{book_id}/{chapter}/")
                verses = [{"verse": r["verse"], "text": strip_markup(r["text"])} for r in rows]
            elif source["kind"] == "getbible":
                data = get_json(f"https://api.getbible.net/v2/{source['id']}/{book_id}/{chapter}.json")
                verses = [{"verse": r["verse"], "text": r["text"]} for r in data.get("verses") or []]
            else:
                continue
            if verses:
                return lang, book, verses
        except Exception as err:  # noqa: BLE001
            errors.append(f"{source['kind']}:{err}")
    raise RuntimeError("no verses: " + " · ".join(errors))


def print_html(lang: dict, book: dict, chapter: int, verses: list[dict], source_name: str) -> str:
    title = f"{book['name']} {chapter}"
    pages = [verses[i : i + 12] for i in range(0, len(verses), 12)] or [[]]
    sheets = []
    for index, part in enumerate(pages, start=1):
        body = "\n".join(
            f'<p class="v"><sup>{v["verse"]}</sup> {html.escape(v["text"])}</p>' for v in part
        )
        heading = title if index == 1 else f"{title} (cont.)"
        sheets.append(
            f"""
<section class="sheet">
  <header class="mark"><span>{SITE}</span><span>{html.escape(title)} · p.{index}</span></header>
  <div class="body">
    <h1>{html.escape(heading)}</h1>
    <p class="meta">{html.escape(lang["native"])} / {html.escape(lang["name"])} · {html.escape(source_name)} · {BRAND}</p>
    {body}
  </div>
  <footer class="mark"><span>{SITE}</span><span>{CREDIT}</span></footer>
</section>
"""
        )
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang["iso"])}" dir="{"rtl" if lang.get("rtl") else "ltr"}">
<head>
<meta charset="utf-8" />
<title>{html.escape(title)} · {SITE}</title>
<style>
  @page {{ size: 6in 9in; margin: 0; }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0;
    padding: 0;
    background: #fff;
    color: #1a1510;
    font-family: "Times New Roman", Georgia, serif;
  }}
  .sheet {{
    width: 6in;
    height: 9in;
    padding: 12mm 14mm 10mm;
    display: flex;
    flex-direction: column;
    page-break-after: always;
    break-after: page;
  }}
  .sheet:last-child {{ page-break-after: auto; break-after: auto; }}
  .mark {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    font-family: "Courier New", ui-monospace, monospace;
    font-size: 8.5pt;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #6a5420;
    border-color: #d7cbb3;
  }}
  header.mark {{ border-bottom: 1px solid #d7cbb3; padding-bottom: 6pt; }}
  footer.mark {{ border-top: 1px solid #d7cbb3; padding-top: 6pt; margin-top: auto; }}
  .body {{ flex: 1; padding: 10pt 0 8pt; }}
  h1 {{
    font-size: 18pt;
    font-weight: 600;
    margin: 0 0 6pt;
    text-align: center;
  }}
  .meta {{
    text-align: center;
    font-family: "Courier New", ui-monospace, monospace;
    font-size: 8pt;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7a5a12;
    margin: 0 0 12pt;
  }}
  .v {{
    margin: 0 0 7pt;
    font-size: 11pt;
    line-height: 1.45;
    text-align: justify;
  }}
  .v sup {{
    font-family: "Courier New", ui-monospace, monospace;
    font-size: 7.5pt;
    color: #7a5a12;
    margin-right: 4pt;
  }}
</style>
</head>
<body>
{''.join(sheets)}
</body>
</html>
"""


def chrome_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = "google-chrome"
    cmd = [
        chrome,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-pdf-header-footer",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={pdf_path.parent / '.chrome-profile'}",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, check=False, timeout=20, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        subprocess.run(["pkill", "-f", f"print-to-pdf={pdf_path}"], check=False)
    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        raise RuntimeError(f"chrome did not write {pdf_path}")


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def build_pdf(iso: str, book_id: int, chapter: int, out_dir: Path) -> Path:
    lang, book, verses = load_verses(iso, book_id, chapter)
    source_name = (lang["sources"][0].get("name") if lang.get("sources") else "Open text") or "Open text"
    markup = print_html(lang, book, chapter, verses, source_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"ChristSupply.Net-{slug(lang['name'])}-{slug(book['name'])}-{chapter}.pdf"
    pdf_path = out_dir / name
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "chapter.html"
        html_path.write_text(markup, encoding="utf-8")
        chrome_pdf(html_path, pdf_path)
    return pdf_path


def render_pages(pdf_path: Path, image_dir: Path, stem: str) -> list[Path]:
    import pypdfium2 as pdfium

    image_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    paths = []
    for index, page in enumerate(pdf, start=1):
        pil = page.render(scale=2.2).to_pil()
        out = image_dir / f"{stem}-page-{index}.png"
        pil.save(out, "PNG")
        paths.append(out)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso", default="eng")
    parser.add_argument("--book", type=int, default=1)
    parser.add_argument("--chapter", type=int, default=1)
    parser.add_argument("--out", default=str(ROOT / "pdfs"))
    parser.add_argument("--samples", action="store_true")
    args = parser.parse_args()
    out_dir = Path(args.out)
    jobs = [(args.iso, args.book, args.chapter)]
    if args.samples:
        jobs = [
            ("eng", 1, 1),
            ("eng", 43, 3),
            ("eng", 40, 5),
            ("spa", 1, 1),
        ]
    for iso, book_id, chapter in jobs:
        path = build_pdf(iso, book_id, chapter, out_dir)
        print(path)


if __name__ == "__main__":
    main()
