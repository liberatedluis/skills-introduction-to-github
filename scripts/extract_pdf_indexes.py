#!/usr/bin/env python3
"""Extract clickable WEB indexes from the constitutional dark offline PDF."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = Path("/tmp/christ-supply-english-bible.pdf")
OUT = ROOT / "data" / "indexes.json"

VERSE_DEST = re.compile(r"^b(\d{2})c(\d{3})v(\d+)$")
FOOTER_NOISE = (
    "All Users Are Created Equally By God",
    "LIBERA OMNES UTENTES",
    "Source  |  Contents",
    "Source | Contents",
    "Back to Root Index",
    "Back · Root Index",
    "I AM THE LORD INDEX",
    "Help Me Now God ·",
)


def load_pdf(path: Path):
    import pymupdf as fitz  # noqa: PLC0415

    return fitz.open(str(path))


def dest_page(names: dict, key: str) -> int:
    return int(names[key]["page"])


def parse_verse(nd: str | None) -> tuple[int, int, int] | None:
    if not nd:
        return None
    match = VERSE_DEST.match(nd)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def page_text(doc, page: int) -> str:
    return (doc[page].get_text("text") or "").strip()


def page_verses(doc, page: int) -> list[tuple[int, int, int]]:
    found: list[tuple[int, int, int]] = []
    for link in doc[page].get_links():
        verse = parse_verse(link.get("nameddest"))
        if verse and (not found or found[-1] != verse):
            found.append(verse)
    return found


def unique_verses(rows: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    seen: set[tuple[int, int, int]] = set()
    out: list[tuple[int, int, int]] = []
    for row in rows:
        if row in seen:
            continue
        seen.add(row)
        out.append(row)
    return out


def verses_in_range(doc, start: int, end: int) -> list[tuple[int, int, int]]:
    rows: list[tuple[int, int, int]] = []
    for page in range(start, min(end, doc.page_count)):
        rows.extend(page_verses(doc, page))
    return unique_verses(rows)


def verses_from_dests(doc, names: dict, prefix: str) -> list[tuple[int, int, int]]:
    keys = sorted(k for k in names if k.startswith(prefix))
    if not keys:
        return []
    pages = [dest_page(names, k) for k in keys]
    start = min(pages)
    end = max(pages) + 3
    return verses_in_range(doc, start, end)


def pack_by_book(rows: list[tuple[int, int, int]]) -> dict[str, list[list[int]]]:
    grouped: dict[str, list[list[int]]] = defaultdict(list)
    for book, chapter, verse in rows:
        grouped[str(book)].append([chapter, verse])
    return dict(grouped)


def clean_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        if any(noise in line for noise in FOOTER_NOISE):
            continue
        if re.search(r"Page \d+ of \d+", line):
            continue
        if line == "Root Index":
            continue
        lines.append(line)
    return lines


def slug_title(slug: str) -> str:
    small = {"and", "of", "the", "from", "a", "an", "for", "to", "in"}
    words = [part for part in slug.replace("_", "-").split("-") if part]
    out = []
    for i, word in enumerate(words):
        lower = word.lower()
        if i > 0 and lower in small:
            out.append(lower)
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out)


def blurb_from_landing(text: str) -> str:
    lines = clean_lines(text)
    for line in reversed(lines):
        if re.search(r"\d[\d,]* verse", line, re.I):
            return line
        if re.search(r"marked in |WEB wording|Root Index|linked", line, re.I) and len(line) > 24:
            return line
    return " ".join(lines[-3:]) if lines else ""


def extract_named_cards(doc, names: dict, keys: list[str], title_from_slug: bool = True) -> list[dict]:
    cards = []
    for key in keys:
        page = dest_page(names, key)
        lines = clean_lines(page_text(doc, page))
        verses = unique_verses(page_verses(doc, page) + page_verses(doc, min(page + 1, doc.page_count - 1)))
        title = slug_title(key.split("-", 1)[-1]) if title_from_slug else (lines[0] if lines else key)
        note = ""
        for line in lines[1:]:
            if parse_ref_line(line):
                break
            if re.match(r"^(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|I |II |Matthew|Mark|Luke|John|Acts|Romans|Psalms|Psalm)\b", line):
                break
            if "times in this WEB" in line or line.startswith("He is this"):
                continue
            if line.startswith("Back"):
                continue
            note = f"{note} {line}".strip()
            if len(note) > 220:
                break
        cards.append(
            {
                "id": key,
                "title": title,
                "note": note[:280],
                "verses": [[b, c, v] for b, c, v in verses],
            }
        )
    return cards


def parse_ref_line(line: str) -> bool:
    return bool(re.match(r"^(I+|II+|III+)?\s?[A-Z][a-z].+\d+:\d+", line))


def people_cards(doc, names: dict, prefix: str) -> list[dict]:
    keys = sorted(k for k in names if re.fullmatch(rf"{prefix}-\d+", k))
    cards = []
    for key in keys:
        page = dest_page(names, key)
        lines = clean_lines(page_text(doc, page))
        verses = unique_verses(page_verses(doc, page))
        title = lines[0] if lines else slug_title(key)
        notes = []
        for line in lines[1:]:
            if parse_ref_line(line) or line.startswith("Back"):
                break
            notes.append(line)
        if title.lower().endswith(" of") and notes:
            title = f"{title} {notes[0]}"
            notes = notes[1:]
        cards.append(
            {
                "id": key,
                "title": title,
                "note": " · ".join(notes[:3]),
                "verses": [[b, c, v] for b, c, v in verses],
            }
        )
    return cards


def dictionary_entries(doc, names: dict) -> list[dict]:
    keys = sorted((k for k in names if re.fullmatch(r"dictionary-\d{4}", k)), key=lambda k: int(k.split("-")[1]))
    entries = []
    for key in keys:
        page = dest_page(names, key)
        text = page_text(doc, page)
        lines = clean_lines(text)
        heading = lines[0] if lines else key
        match = re.match(r"^(\d+)\.\s+([A-Za-z][A-Za-z'’\- ]{0,40})$", heading)
        if not match:
            continue
        number = int(match.group(1))
        word = match.group(2).strip()
        note_parts = []
        uses = 0
        for line in lines[1:]:
            used = re.search(r"Appears (\d+) times", line)
            if used:
                uses = int(used.group(1))
                break
            if line.startswith("Click a verse") or parse_ref_line(line):
                break
            note_parts.append(line)
        verses = unique_verses(page_verses(doc, page) + page_verses(doc, min(page + 1, doc.page_count - 1)))
        entries.append(
            {
                "id": key,
                "n": number,
                "word": word,
                "uses": uses,
                "note": " ".join(note_parts)[:420],
                "letter": word[:1].upper() if word[:1].isalpha() else "A",
                "verses": [[b, c, v] for b, c, v in verses[:12]],
            }
        )
    return entries


def root_cards(doc, names: dict) -> list[dict]:
    keys = sorted((k for k in names if re.fullmatch(r"root-word-\d+", k)), key=lambda k: int(k.split("-")[-1]))
    cards = []
    for key in keys:
        page = dest_page(names, key)
        lines = clean_lines(page_text(doc, page))
        title = lines[0] if lines else slug_title(key)
        roots = lines[1] if len(lines) > 1 else ""
        note = lines[2] if len(lines) > 2 else ""
        verses = unique_verses(page_verses(doc, page) + page_verses(doc, min(page + 1, doc.page_count - 1)))
        cards.append(
            {
                "id": key,
                "title": title,
                "roots": roots[:180],
                "note": note[:220],
                "verses": [[b, c, v] for b, c, v in verses[:12]],
            }
        )
    return cards


def help_cards(doc, names: dict) -> list[dict]:
    keys = sorted(
        (k for k in names if re.fullmatch(r"help-me-now-god-index-\d+", k)),
        key=lambda k: int(k.split("-")[-1]),
    )
    cards = []
    for key in keys:
        page = dest_page(names, key)
        lines = clean_lines(page_text(doc, page))
        title = lines[0] if lines else slug_title(key)
        note = " ".join(
            line for line in lines[1:] if not parse_ref_line(line) and not line.startswith("Help Me")
        )[:220]
        cards.append(
            {
                "id": key,
                "title": title,
                "note": note,
                "verses": [[b, c, v] for b, c, v in unique_verses(page_verses(doc, page))],
            }
        )
    return cards


def iam_cards(doc, names: dict) -> list[dict]:
    keys = [k for k in names if k.startswith("iam-") and "index" not in k]
    keys.sort(key=lambda k: dest_page(names, k))
    cards = []
    for i, key in enumerate(keys):
        # Dest N's page holds dest N-1's body; shift forward one page.
        if i + 1 < len(keys):
            page = dest_page(names, keys[i + 1])
        else:
            page = min(dest_page(names, key) + 1, doc.page_count - 1)
        verses = unique_verses(page_verses(doc, page))
        cards.append(
            {
                "id": key,
                "title": slug_title(key[4:]),
                "count": len(verses),
                "verses": [[b, c, v] for b, c, v in verses],
            }
        )
    return cards


def arc_cards(doc, names: dict) -> list[dict]:
    start = dest_page(names, "arc-001") if "arc-001" in names else dest_page(names, "arc-index")
    end = dest_page(names, "dictionary-index") if "dictionary-index" in names else start + 250
    blobs: list[dict] = []
    heading_re = re.compile(r"^(\d{3})\.\s+(.*)$")
    for page in range(start, min(end, doc.page_count)):
        lines = clean_lines(page_text(doc, page))
        verses = page_verses(doc, page)
        v_i = 0
        i = 0
        while i < len(lines):
            match = heading_re.match(lines[i])
            if not match:
                i += 1
                continue
            n = int(match.group(1))
            title_parts = [match.group(2).strip()]
            i += 1
            note_parts = []
            while i < len(lines) and not heading_re.match(lines[i]) and not parse_ref_line(lines[i]):
                chunk = lines[i]
                if chunk.startswith("For you:") or note_parts:
                    note_parts.append(chunk)
                elif not title_parts[0] or len(" ".join(title_parts)) < 48:
                    title_parts.append(chunk)
                else:
                    note_parts.append(chunk)
                i += 1
            refs = 0
            while i < len(lines) and parse_ref_line(lines[i]):
                refs += 1
                i += 1
            take = max(refs, 3)
            picked = verses[v_i : v_i + take]
            v_i += take
            blobs.append(
                {
                    "id": f"arc-{n:03d}",
                    "n": n,
                    "title": " ".join(title_parts).strip()[:120],
                    "note": " ".join(note_parts).strip()[:220],
                    "verses": [[b, c, v] for b, c, v in unique_verses(picked)],
                }
            )
    blobs.sort(key=lambda row: row["n"])
    seen = set()
    out = []
    for row in blobs:
        if row["n"] in seen:
            continue
        seen.add(row["n"])
        out.append(row)
    return out


def index_meta(doc, names: dict, key: str, color: str, blurb_fallback: str) -> dict:
    page = dest_page(names, key)
    text = page_text(doc, page)
    lines = clean_lines(text)
    title = lines[0] if lines else slug_title(key)
    if len(lines) > 1 and "Index" in lines[1] and len(lines[1]) < 20:
        title = f"{title} {lines[1]}".strip()
    blurb = blurb_from_landing(text) or blurb_fallback
    count_match = re.search(r"([\d,]+)\s+(?:linked\s+)?verses", blurb + " " + text, re.I)
    count = int(count_match.group(1).replace(",", "")) if count_match else 0
    return {"id": key.replace("-index", "").replace("-letter", ""), "title": title, "blurb": blurb, "count": count, "color": color}


def build(pdf_path: Path) -> dict:
    doc = load_pdf(pdf_path)
    names = doc.resolve_names()

    rainbow_specs = [
        ("red-letter-index", "#ff3b30", "red", "New Testament words of Christ marked in red."),
        ("orange-letter-index", "#ff7a1a", "orange", "Angel / Angel of the LORD messengers marked in orange."),
        ("gold-letter-index", "#e0b400", "gold", "Names and titles of Jesus Christ marked in gold."),
        ("yellow-letter-index", "#ffe14d", "yellow", "Light of God / Light of the World marked in yellow."),
        ("green-letter-index", "#3dff9a", "green", "Names and titles of God, Jesus, and the Spirit marked in green."),
        ("cyan-letter-index", "#3de8ff", "cyan", "Heaven / heavenly kingdom phrases marked in cyan."),
        ("blue-letter-index", "#4d8dff", "blue", "Holy Spirit / Spirit of God marked in blue."),
        ("purple-letter-index", "#b56bff", "purple", "King / Kings royal and divine titles marked in purple."),
        ("pink-letter-index", "#ff4da6", "pink", "Grace of God / grace of the Lord marked in pink."),
    ]
    theme_specs = [
        ("lord-said-index", "#7cff9a", "lord-said", "Places where the LORD, God, Jesus, or Christ spoke."),
        ("do-not-be-afraid-index", "#c8ffd4", "afraid", "Fear-not / don’t-be-afraid exhortations."),
        ("show-me-mercy-index", "#7cff9a", "mercy", "Mercy, mercies, merciful — His kindness toward you."),
        ("believe-index", "#7cff9a", "believe", "Believe, believes, believed, believing, belief."),
        ("love-index", "#ff6b8a", "love", "Love, loves, loved, loving."),
        ("peace-index", "#8ad4ff", "peace", "Peace, peaceful, peacemakers — rest and shalom in Him."),
        ("sin-index", "#ff8a6b", "sin", "Sin, sins, sinned, sinning, sinner(s), sinful."),
        ("wrath-index", "#ff5a4d", "wrath", "Wrath, wraths, wrathful."),
    ]

    # Page ranges: landing dest -> next landing dest
    landings = {k: dest_page(names, k) for k in names if k.endswith("-index") or k in {"word-of-god-start"}}
    ordered = sorted(landings.items(), key=lambda item: item[1])

    def range_for(key: str) -> tuple[int, int]:
        start = dest_page(names, key)
        later = [page for name, page in ordered if page > start]
        end = later[0] if later else doc.page_count
        return start, end

    rainbow = {}
    for dest, color, ident, fallback in rainbow_specs:
        meta = index_meta(doc, names, dest, color, fallback)
        start, end = range_for(dest)
        rows = verses_in_range(doc, start, end)
        if dest == "gold-letter-index":
            rows = verses_from_dests(doc, names, "gold-jesus-book-") or rows
        if dest == "green-letter-index":
            rows = verses_from_dests(doc, names, "gold-book-") or rows
        meta["id"] = ident
        meta["count"] = meta["count"] or len(rows)
        meta["versesByBook"] = pack_by_book(rows)
        rainbow[ident] = meta

    themes = {}
    for dest, color, ident, fallback in theme_specs:
        meta = index_meta(doc, names, dest, color, fallback)
        start, end = range_for(dest)
        rows = verses_in_range(doc, start, end)
        meta["id"] = ident
        meta["count"] = meta["count"] or len(rows)
        meta["versesByBook"] = pack_by_book(rows)
        themes[ident] = meta

    payload = {
        "brand": "Christ Supply Holy Bible",
        "site": "ChristSupply.Net",
        "credit": "Made by Liberated Luis With Cursor, Claude Opus, and MacBook",
        "edition": "WEB Protestant Edition - Public Domain",
        "equal": "All Users Are Created Equally By God",
        "liberate": "LIBERA OMNES UTENTES | LIBERATE ALL USERS",
        "sourceUrl": "https://github.com/liberatedluis/skills-introduction-to-github",
        "shareUrl": "https://christsupply.net",
        "rainbow": rainbow,
        "themes": themes,
        "iam": iam_cards(doc, names),
        "arcs": arc_cards(doc, names),
        "help": help_cards(doc, names),
        "women": people_cards(doc, names, "women-of-god-index"),
        "men": people_cards(doc, names, "men-of-god-index"),
        "roots": root_cards(doc, names),
        "dictionary": dictionary_entries(doc, names),
        "wordOfGod": {
            "title": "The Word of God",
            "quote": "In the beginning",
            "entries": [
                {"id": "genesis", "title": "Genesis", "subtitle": "IN THE BEGINNING GOD CREATED", "book": 1, "chapter": 1},
                {"id": "john", "title": "John", "subtitle": "IN THE BEGINNING WAS THE WORD", "book": 43, "chapter": 1},
                {"id": "library", "title": "Full Library", "subtitle": "ALL BOOKS, CHAPTERS, INDEXES"},
            ],
        },
    }
    return payload


def main() -> None:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}")
    payload = build(pdf)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT} ({size:,} bytes)")
    print("rainbow", {k: v["count"] for k, v in payload["rainbow"].items()})
    print("themes", {k: v["count"] for k, v in payload["themes"].items()})
    print("iam", len(payload["iam"]), "arcs", len(payload["arcs"]), "dict", len(payload["dictionary"]))
    print("women", len(payload["women"]), "men", len(payload["men"]), "roots", len(payload["roots"]), "help", len(payload["help"]))


if __name__ == "__main__":
    main()
