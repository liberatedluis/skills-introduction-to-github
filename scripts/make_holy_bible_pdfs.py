#!/usr/bin/env python3
"""Generate 1300 print-ready Christ Supply Holy Bible PDFs (6x9, mark on every page)."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import BRAND, CREDIT, SITE, SITE_URL  # noqa: E402

NOTO = Path("/usr/share/fonts/truetype/noto")
CJK = Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
CSV_PATH = ROOT / "data" / "ebible-translations.csv"
BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
BOOK_NAMES = {row["usfm"]: row["name"] for row in BOOKS}
CACHE = ROOT / ".cache" / "vpl"
OUT_DIR = ROOT / "pdfs" / "holy-bibles"
UA = {"User-Agent": "ChristSupplyHolyBible/1.0"}

VPL_LINE = re.compile(r"^(\S+)\s+(\d+):(\d+)\s+(.*)$")

SCRIPT_ALIASES = {
    "latin": "Latin",
    "cyrillic": "Cyrillic",
    "greek": "Greek",
    "arabic": "Arabic",
    "hebrew": "Hebrew",
    "devanagari": "Devanagari",
    "devanagari (nagari)": "Devanagari",
    "bengali": "Bengali",
    "tamil": "Tamil",
    "telugu": "Telugu",
    "malayalam": "Malayalam",
    "kannada": "Kannada",
    "gujarati": "Gujarati",
    "oriya": "Oriya",
    "gurmukhi": "Gurmukhi",
    "thai": "Thai",
    "ethiopic": "Ethiopic",
    "ethiopic (geʻez)": "Ethiopic",
    "ethiopic (ge'ez)": "Ethiopic",
    "amheric": "Ethiopic",
    "amharic": "Ethiopic",
    "tibetan": "Tibetan",
    "syriac": "Syriac",
    "coptic": "Coptic",
    "sinhala": "Sinhala",
    "georgian": "Georgian",
    "armenian": "Armenian",
    "thaana": "Thaana",
    "cherokee": "Cherokee",
    "cjk": "CJK",
    "chinese": "CJK",
    "han (simplified variant)": "CJK",
    "han (traditional variant)": "CJK",
    "tifenagh": "Tifinagh",
    "tifinagh": "Tifinagh",
    "burmese": "Myanmar",
    "myanmar": "Myanmar",
    "gothic": "Gothic",
    "khmer": "Khmer",
    "lao": "Lao",
    "latin (roman) with papua new guinea enhancements": "Latin",
    "code for uncoded script": "Latin",
    "code for inherited script": "Latin",
}

SCRIPT_FONTS = {
    "Latin": NOTO / "NotoSerif-Regular.ttf",
    "Cyrillic": NOTO / "NotoSerif-Regular.ttf",
    "Greek": NOTO / "NotoSerif-Regular.ttf",
    "Arabic": NOTO / "NotoNaskhArabic-Regular.ttf",
    "Hebrew": NOTO / "NotoSerifHebrew-Regular.ttf",
    "Devanagari": NOTO / "NotoSerifDevanagari-Regular.ttf",
    "Bengali": NOTO / "NotoSerifBengali-Regular.ttf",
    "Tamil": NOTO / "NotoSerifTamil-Regular.ttf",
    "Telugu": NOTO / "NotoSerifTelugu-Regular.ttf",
    "Malayalam": NOTO / "NotoSerifMalayalam-Regular.ttf",
    "Kannada": NOTO / "NotoSerifKannada-Regular.ttf",
    "Gujarati": NOTO / "NotoSerifGujarati-Regular.ttf",
    "Oriya": NOTO / "NotoSansOriya-Regular.ttf",
    "Gurmukhi": NOTO / "NotoSerifGurmukhi-Regular.ttf",
    "Thai": NOTO / "NotoSerifThai-Regular.ttf",
    "Ethiopic": NOTO / "NotoSerifEthiopic-Regular.ttf",
    "Tibetan": NOTO / "NotoSerifTibetan-Regular.ttf",
    "Syriac": NOTO / "NotoSansSyriac-Regular.ttf",
    "Coptic": NOTO / "NotoSansCoptic-Regular.ttf",
    "Sinhala": NOTO / "NotoSerifSinhala-Regular.ttf",
    "Georgian": NOTO / "NotoSerifGeorgian-Regular.ttf",
    "Armenian": NOTO / "NotoSerifArmenian-Regular.ttf",
    "Thaana": NOTO / "NotoSansThaana-Regular.ttf",
    "Cherokee": NOTO / "NotoSansCherokee-Regular.ttf",
    "CJK": CJK,
    "Tifinagh": NOTO / "NotoSansTifinagh-Regular.ttf",
    "Myanmar": NOTO / "NotoSerifMyanmar-Regular.ttf",
    "Gothic": NOTO / "NotoSansGothic-Regular.ttf",
    "Khmer": NOTO / "NotoSerifKhmer-Regular.ttf",
    "Lao": NOTO / "NotoSerifLao-Regular.ttf",
}

FALLBACK_FILES = [
    ("FbHebrew", NOTO / "NotoSerifHebrew-Regular.ttf"),
    ("FbHebrewSans", NOTO / "NotoSansHebrew-Regular.ttf"),
    ("FbArabic", NOTO / "NotoNaskhArabic-Regular.ttf"),
    ("FbNastaliq", NOTO / "NotoNastaliqUrdu-Regular.ttf"),
    ("FbDevanagari", NOTO / "NotoSerifDevanagari-Regular.ttf"),
    ("FbBengali", NOTO / "NotoSerifBengali-Regular.ttf"),
    ("FbGujarati", NOTO / "NotoSerifGujarati-Regular.ttf"),
    ("FbGurmukhi", NOTO / "NotoSerifGurmukhi-Regular.ttf"),
    ("FbOriya", NOTO / "NotoSansOriya-Regular.ttf"),
    ("FbTamil", NOTO / "NotoSerifTamil-Regular.ttf"),
    ("FbTelugu", NOTO / "NotoSerifTelugu-Regular.ttf"),
    ("FbKannada", NOTO / "NotoSerifKannada-Regular.ttf"),
    ("FbMalayalam", NOTO / "NotoSerifMalayalam-Regular.ttf"),
    ("FbSinhala", NOTO / "NotoSerifSinhala-Regular.ttf"),
    ("FbThai", NOTO / "NotoSerifThai-Regular.ttf"),
    ("FbLao", NOTO / "NotoSerifLao-Regular.ttf"),
    ("FbTibetan", NOTO / "NotoSerifTibetan-Regular.ttf"),
    ("FbMyanmar", NOTO / "NotoSerifMyanmar-Regular.ttf"),
    ("FbKhmer", NOTO / "NotoSerifKhmer-Regular.ttf"),
    ("FbEthiopic", NOTO / "NotoSerifEthiopic-Regular.ttf"),
    ("FbArmenian", NOTO / "NotoSerifArmenian-Regular.ttf"),
    ("FbGeorgian", NOTO / "NotoSerifGeorgian-Regular.ttf"),
    ("FbSyriac", NOTO / "NotoSansSyriac-Regular.ttf"),
    ("FbCoptic", NOTO / "NotoSansCoptic-Regular.ttf"),
    ("FbThaana", NOTO / "NotoSansThaana-Regular.ttf"),
    ("FbCherokee", NOTO / "NotoSansCherokee-Regular.ttf"),
    ("FbTifinagh", NOTO / "NotoSansTifinagh-Regular.ttf"),
    ("FbGothic", NOTO / "NotoSansGothic-Regular.ttf"),
    ("FbSymbols", NOTO / "NotoSansSymbols2-Regular.ttf"),
    ("CJK", CJK),
]

UNICODE_RANGES = (
    ("Hebrew", 0x0590, 0x05FF),
    ("Arabic", 0x0600, 0x06FF),
    ("Arabic", 0x0750, 0x077F),
    ("Arabic", 0x08A0, 0x08FF),
    ("Arabic", 0xFB50, 0xFDFF),
    ("Syriac", 0x0700, 0x074F),
    ("Thaana", 0x0780, 0x07BF),
    ("Devanagari", 0x0900, 0x097F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Oriya", 0x0B00, 0x0B7F),
    ("Tamil", 0x0B80, 0x0BFF),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Malayalam", 0x0D00, 0x0D7F),
    ("Sinhala", 0x0D80, 0x0DFF),
    ("Thai", 0x0E00, 0x0E7F),
    ("Lao", 0x0E80, 0x0EFF),
    ("Tibetan", 0x0F00, 0x0FFF),
    ("Myanmar", 0x1000, 0x109F),
    ("Ethiopic", 0x1200, 0x137F),
    ("Cherokee", 0x13A0, 0x13FF),
    ("Khmer", 0x1780, 0x17FF),
    ("Georgian", 0x10A0, 0x10FF),
    ("Armenian", 0x0530, 0x058F),
    ("Coptic", 0x2C80, 0x2CFF),
    ("Tifinagh", 0x2D30, 0x2D7F),
    ("Gothic", 0x10330, 0x1034F),
    ("CJK", 0x3040, 0x30FF),
    ("CJK", 0x3400, 0x4DBF),
    ("CJK", 0x4E00, 0x9FFF),
    ("CJK", 0xAC00, 0xD7AF),
)

GETBIBLE_EXTRAS = [
    {"id": "che1860", "title": "Cherokee New Testament 1860", "language": "Cherokee", "script": "Cherokee", "rtl": False},
    {"id": "gothic", "title": "Gothic Bible portions", "language": "Gothic", "script": "Gothic", "rtl": False},
    {"id": "sahidic", "title": "Sahidic Coptic New Testament", "language": "Coptic", "script": "Coptic", "rtl": False},
    {"id": "manxgaelic", "title": "Manx Gaelic Bible portions", "language": "Manx Gaelic", "script": "Latin", "rtl": False},
    {"id": "potawatomi", "title": "Potawatomi Matthew and Acts 1844", "language": "Potawatomi", "script": "Latin", "rtl": False},
    {"id": "calo", "title": "Caló Gospel of Luke", "language": "Caló", "script": "Latin", "rtl": False},
    {"id": "gaelic", "title": "Scots Gaelic Gospel of Mark", "language": "Scottish Gaelic", "script": "Latin", "rtl": False},
    {"id": "peshitta", "title": "Syriac Peshitta New Testament", "language": "Syriac", "script": "Syriac", "rtl": True},
    {"id": "basque", "title": "Basque Navarro-Labourdin New Testament", "language": "Basque", "script": "Latin", "rtl": False},
]


def verses_of(row: dict) -> int:
    def n(key: str) -> int:
        try:
            return int(row.get(key) or 0)
        except ValueError:
            return 0

    return n("OTverses") + n("NTverses") + n("DCverses")


def coverage_of(row: dict) -> str:
    try:
        ot, nt = int(row.get("OTbooks") or 0), int(row.get("NTbooks") or 0)
    except ValueError:
        return "portions"
    if ot >= 39 and nt >= 27:
        return "bible"
    if nt >= 27:
        return "nt"
    return "portions"


def fetch(url: str) -> bytes:
    req = Request(url, headers=UA)
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def build_catalog() -> list[dict]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    catalog = []
    for row in rows:
        if row.get("Redistributable") != "True" or row.get("downloadable") != "True":
            continue
        if verses_of(row) < 1:
            continue
        catalog.append(
            {
                "id": row["translationId"],
                "source": "ebible",
                "title": row.get("title") or row["translationId"],
                "language": row.get("languageNameInEnglish") or row.get("languageName") or "",
                "native": row.get("languageName") or "",
                "iso": row.get("languageCode") or "",
                "script": row.get("script") or "Latin",
                "rtl": (row.get("textDirection") or "").lower() == "rtl",
                "copyright": row.get("Copyright") or "",
                "verses": verses_of(row),
                "coverage": coverage_of(row),
            }
        )
    catalog.sort(key=lambda r: (-r["verses"], r["language"], r["id"]))
    have = {r["id"].lower() for r in catalog}
    for extra in GETBIBLE_EXTRAS:
        if extra["id"].lower() in have:
            continue
        catalog.append(
            {
                **extra,
                "source": "getbible",
                "native": extra["language"],
                "iso": extra["id"][:3],
                "copyright": "Public Domain",
                "verses": 0,
                "coverage": "portions",
            }
        )
        if len(catalog) >= 1300:
            break
    if len(catalog) > 1300:
        catalog = catalog[:1300]
    if len(catalog) < 1300:
        raise SystemExit(f"only {len(catalog)} open translations available")
    return catalog


def parse_vpl(text: str) -> list[tuple[str, int, int, str]]:
    verses = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = VPL_LINE.match(line)
        if not match:
            continue
        book, chapter, verse, body = match.groups()
        book = book.upper()
        if book in {"FRT", "INT", "GLO", "XXA", "XXB", "XXC", "XXD", "XXE", "XXF", "XXG"}:
            continue
        verses.append((book, int(chapter), int(verse), body.strip()))
    return verses


def load_ebible_verses(translation_id: str) -> list[tuple[str, int, int, str]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    zpath = CACHE / f"{translation_id}_vpl.zip"
    if not zpath.exists() or zpath.stat().st_size < 64:
        data = fetch(f"https://ebible.org/Scriptures/{translation_id}_vpl.zip")
        zpath.write_bytes(data)
    with zipfile.ZipFile(zpath) as zf:
        names = [n for n in zf.namelist() if n.endswith("_vpl.txt") or n.endswith(".txt")]
        if not names:
            raise RuntimeError("no vpl txt")
        payload = zf.read(names[0]).decode("utf-8", errors="replace")
    verses = parse_vpl(payload)
    if not verses:
        raise RuntimeError("empty vpl")
    return verses


def load_getbible_verses(translation_id: str) -> list[tuple[str, int, int, str]]:
    data = json.loads(fetch(f"https://api.getbible.net/v2/{translation_id}.json").decode("utf-8"))
    verses = []
    books = data.get("books") or data
    if isinstance(books, dict) and "verses" not in books:
        iterable = books.values() if all(isinstance(v, dict) for v in books.values()) else []
        for book in iterable:
            usfm = None
            name = book.get("name") or ""
            nr = book.get("nr") or book.get("book_nr")
            if isinstance(nr, int) and 1 <= nr <= 66:
                usfm = BOOKS[nr - 1]["usfm"]
            chapters = book.get("chapters") or {}
            if isinstance(chapters, dict):
                chapter_iter = chapters.values()
            else:
                chapter_iter = chapters
            for chapter in chapter_iter:
                ch = int(chapter.get("chapter") or chapter.get("nr") or 0)
                for verse in chapter.get("verses") or []:
                    verses.append(
                        (
                            usfm or name or "UNK",
                            int(verse.get("chapter") or ch or 1),
                            int(verse.get("verse") or 0),
                            verse.get("text") or "",
                        )
                    )
    if not verses:
        if isinstance(data, list):
            for row in data:
                verses.append((str(row.get("book") or "UNK"), int(row.get("chapter") or 1), int(row.get("verse") or 1), row.get("text") or ""))
    if not verses:
        raise RuntimeError("could not parse getbible json")
    return verses


def normalize_script(script: str) -> str:
    return SCRIPT_ALIASES.get((script or "Latin").strip().lower(), "Latin")


def detect_script(text: str) -> str:
    counts: Counter[str] = Counter()
    for ch in text:
        code = ord(ch)
        for name, start, end in UNICODE_RANGES:
            if start <= code <= end:
                counts[name] += 1
                break
    if not counts:
        return "Latin"
    return counts.most_common(1)[0][0]


def choose_script(meta: dict, verses: list[tuple[str, int, int, str]]) -> str:
    mapped = normalize_script(meta.get("script") or "Latin")
    sample = " ".join(body for _, _, _, body in verses[:800] if body)
    detected = detect_script(sample[:120000])
    if mapped in {"Latin", "Cyrillic", "Greek"} and detected not in {"Latin", "Cyrillic", "Greek"}:
        return detected
    if mapped in SCRIPT_FONTS:
        return mapped
    return detected


def font_for(script: str) -> Path:
    path = SCRIPT_FONTS.get(normalize_script(script), SCRIPT_FONTS["Latin"])
    if path.exists():
        return path
    latin = SCRIPT_FONTS["Latin"]
    return latin if latin.exists() else path


def pdf_complete(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 1000:
        return False
    with path.open("rb") as handle:
        handle.seek(max(0, path.stat().st_size - 2048))
        tail = handle.read()
    return b"%%EOF" in tail


class HolyBiblePDF(FPDF):
    def __init__(self, running: str, body_font: Path, rtl: bool = False):
        super().__init__(unit="mm", format=(152.4, 228.6))  # 6x9 in
        self.running = running[:48]
        self.rtl = rtl
        self.show_marks = False
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(14, 16, 14)
        self.add_font("Brand", "", str(NOTO / "NotoSerif-Regular.ttf"))
        self.add_font("Body", "", str(body_font))
        fallback_names = ["Body"]
        for family, path in FALLBACK_FILES:
            if not path.exists():
                continue
            try:
                self.add_font(family, "", str(path))
                fallback_names.append(family)
            except Exception:
                continue
        self.set_fallback_fonts(fallback_names)
        try:
            self.set_text_shaping(True, direction="rtl" if rtl else "ltr")
        except Exception:
            pass

    def header(self):
        if not self.show_marks:
            return
        self.set_font("Brand", size=7)
        self.set_text_color(106, 84, 32)
        self.set_y(8)
        width = 152.4 - 28
        self.cell(width / 2, 4, SITE, align="L")
        self.cell(width / 2, 4, f"{self.running}  ·  p.{self.page_no()}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(215, 203, 179)
        self.line(14, 13, 152.4 - 14, 13)
        self.set_y(16)
        self.set_text_color(26, 21, 16)

    def footer(self):
        if not self.show_marks:
            return
        self.set_font("Brand", size=6.5)
        self.set_text_color(106, 84, 32)
        self.set_draw_color(215, 203, 179)
        self.line(14, 228.6 - 14, 152.4 - 14, 228.6 - 14)
        self.set_y(228.6 - 13)
        width = 152.4 - 28
        self.cell(width, 3.2, f"{BRAND}  ·  {SITE}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin)
        self.cell(width, 3.2, CREDIT, align="C")


def write_pdf(meta: dict, verses: list[tuple[str, int, int, str]], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    script = choose_script(meta, verses)
    rtl = bool(meta.get("rtl")) or script in {"Arabic", "Hebrew", "Syriac", "Thaana"}
    pdf = HolyBiblePDF(meta["language"] or meta["id"], font_for(script), rtl)
    pdf.set_title(f"{BRAND} — {meta['title']}")
    pdf.set_author(CREDIT)
    pdf.set_creator(f"{BRAND} · {SITE}")

    def _center(doc: HolyBiblePDF, text: str, height: float) -> None:
        doc.set_x(doc.l_margin)
        doc.multi_cell(doc.epw, height, text, align="C")

    pdf.add_page()
    pdf.set_font("Brand", size=11)
    pdf.set_text_color(106, 84, 32)
    pdf.ln(28)
    _center(pdf, SITE.upper(), 8)
    pdf.set_font("Brand", size=18)
    pdf.set_text_color(26, 21, 16)
    _center(pdf, BRAND, 9)
    pdf.ln(4)
    pdf.set_font("Body", size=13)
    _center(pdf, meta["title"], 7)
    pdf.set_font("Body", size=10)
    pdf.set_text_color(106, 84, 32)
    _center(pdf, f"{meta.get('native') or ''} / {meta['language']}".strip(" /"), 6)
    pdf.ln(6)
    pdf.set_font("Brand", size=8)
    _center(pdf, f"{meta['coverage'].upper()} · {len(verses)} verses", 5)
    if meta.get("copyright"):
        pdf.ln(3)
        _center(pdf, meta["copyright"][:400], 4.5)
    pdf.ln(14)
    pdf.set_text_color(26, 21, 16)
    pdf.set_font("Brand", size=9)
    _center(pdf, CREDIT, 5)
    pdf.ln(2)
    pdf.set_font("Brand", size=8)
    pdf.set_text_color(106, 84, 32)
    _center(pdf, SITE_URL, 5)

    pdf.show_marks = True
    current_book = None
    chapter_buf: list[str] = []
    current_chapter = None
    body_align = "R" if rtl else "L"

    def flush_chapter():
        nonlocal chapter_buf
        if not chapter_buf:
            return
        pdf.set_font("Body", size=10)
        pdf.set_text_color(26, 21, 16)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 5, "\n".join(chapter_buf), align=body_align)
        chapter_buf = []

    pdf.add_page()
    for book, chapter, verse, text in verses:
        if not text:
            continue
        if book != current_book or chapter != current_chapter:
            flush_chapter()
        if book != current_book:
            current_book = book
            current_chapter = None
            pdf.set_font("Brand", size=13)
            pdf.set_text_color(26, 21, 16)
            pdf.ln(2)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 7, BOOK_NAMES.get(book, book), align="C")
            pdf.ln(1)
        if chapter != current_chapter:
            current_chapter = chapter
            pdf.set_font("Brand", size=10)
            pdf.set_text_color(106, 84, 32)
            pdf.set_x(pdf.l_margin)
            pdf.cell(pdf.epw, 6, f"{BOOK_NAMES.get(book, book)} {chapter}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        chapter_buf.append(f"{verse}  {text}")
    flush_chapter()
    tmp = dest.with_suffix(".pdf.tmp")
    pdf.output(str(tmp))
    tmp.replace(dest)


def generate_one(meta: dict, dest: Path, force: bool = False) -> dict:
    if not force and pdf_complete(dest):
        return {"id": meta["id"], "status": "exists", "path": str(dest), "bytes": dest.stat().st_size}
    try:
        if meta["source"] == "ebible":
            verses = load_ebible_verses(meta["id"])
        else:
            verses = load_getbible_verses(meta["id"])
        write_pdf(meta, verses, dest)
        return {"id": meta["id"], "status": "ok", "path": str(dest), "bytes": dest.stat().st_size, "verses": len(verses)}
    except Exception as err:  # noqa: BLE001
        tmp = dest.with_suffix(".pdf.tmp")
        if tmp.exists():
            tmp.unlink()
        return {"id": meta["id"], "status": "error", "error": str(err)[:300]}


def write_index(out: Path, catalog: list[dict], results: list[dict]) -> None:
    by_id = {row["id"]: row for row in catalog}
    ok = sum(1 for row in results if row["status"] in {"ok", "exists"})
    items = []
    for row in sorted(results, key=lambda item: item["id"]):
        meta = by_id.get(row["id"], {})
        title = meta.get("title") or row["id"]
        language = meta.get("language") or ""
        items.append(
            f"<li><a href='ChristSupplyHolyBible-{row['id']}.pdf'>{title}</a> — {language} — {row['status']}</li>"
        )
    (out / "index.html").write_text(
        (
            "<!doctype html><meta charset='utf-8'>"
            f"<title>{BRAND}</title>"
            f"<h1>{BRAND}</h1><p>{CREDIT}</p>"
            f"<p>{SITE} · {ok}/{len(results)} print PDFs · 6×9 in</p>"
            f"<ul>{''.join(items)}</ul>"
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--only")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()
    catalog = build_catalog()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "catalog.json").write_text(
        json.dumps(
            {"brand": BRAND, "credit": CREDIT, "site": SITE, "count": len(catalog), "translations": catalog},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    jobs = catalog
    if args.only:
        jobs = [row for row in catalog if row["id"] == args.only]
        if not jobs:
            jobs = [
                {
                    "id": args.only,
                    "source": "ebible",
                    "title": args.only,
                    "language": args.only,
                    "native": args.only,
                    "script": "Latin",
                    "rtl": False,
                    "copyright": "",
                    "coverage": "unknown",
                    "verses": 0,
                }
            ]
    if args.limit:
        jobs = jobs[: args.limit]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(generate_one, meta, out / f"ChristSupplyHolyBible-{meta['id']}.pdf", args.force): meta
            for meta in jobs
        }
        for fut in as_completed(futures):
            result = fut.result()
            results.append(result)
            print(f"{result['status']:6} {result['id']} {result.get('bytes', '')} {result.get('error', '')}", flush=True)
            if len(results) % 25 == 0:
                (out / "progress.json").write_text(
                    json.dumps({"done": len(results), "total": len(jobs), "ok": sum(1 for r in results if r["status"] in {"ok", "exists"})}, indent=2),
                    encoding="utf-8",
                )
    ok = sum(1 for r in results if r["status"] in {"ok", "exists"})
    (out / "build-log.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_index(out, catalog, results)
    print(f"done {ok}/{len(results)} -> {out}")


if __name__ == "__main__":
    main()
