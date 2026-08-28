#!/usr/bin/env python3
"""Put the 1,300 print PDFs in language folders on the Desktop."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import BRAND, CREDIT, SITE, SITE_URL  # noqa: E402

CATALOG = ROOT / "pdfs" / "holy-bibles" / "catalog.json"
PDF_DIR = ROOT / "pdfs" / "holy-bibles"
SAMPLE_DIR = ROOT / "pdfs"
DESKTOP_NAME = BRAND
UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
COVERAGE_LABEL = {
    "bible": "Full Bible",
    "nt": "New Testament",
    "portions": "Portions",
}


def default_desktop() -> Path:
    home = Path.home()
    for candidate in (home / "Desktop", home / "desktop"):
        if candidate.is_dir():
            return candidate / DESKTOP_NAME
    mac = Path("/Users") 
    if mac.is_dir():
        return home / "Desktop" / DESKTOP_NAME
    return home / "Desktop" / DESKTOP_NAME


def safe_name(text: str, fallback: str = "Untitled") -> str:
    cleaned = UNSAFE.sub(" ", (text or "").replace("\n", " ").replace("\r", " "))
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    cleaned = cleaned.rstrip(".")
    if not cleaned or cleaned in {".", ".."}:
        cleaned = fallback
    return cleaned[:120]


def letter_bucket(language: str) -> str:
    for char in language or "":
        if char.isalpha():
            return char.upper() if char.isascii() else "#"
    return "#"


def coverage_label(row: dict) -> str:
    return COVERAGE_LABEL.get(row.get("coverage") or "", "Portions")


def pdf_filename(row: dict, used: set[str]) -> str:
    title = safe_name(row.get("title") or row["id"], row["id"])
    label = coverage_label(row)
    name = f"{label} — {title}.pdf"
    if name in used:
        name = f"{label} — {title} ({row['id']}).pdf"
    if name in used:
        name = f"{label} — {row['id']}.pdf"
    used.add(name)
    return name


def place(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return "exists"
    try:
        os.link(src, dest)
        return "link"
    except OSError:
        shutil.copy2(src, dest)
        return "copy"


def load_catalog() -> list[dict]:
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    return list(payload.get("translations") or [])


def write_readme(dest: Path, count: int, languages: int) -> None:
    text = f"""{BRAND}
{SITE} · {SITE_URL}

{CREDIT}

{count} print-ready Bible PDFs in {languages} language folders.

How to find a Bible
1. Open the letter folder (E for English, S for Spanish, H for Hebrew).
2. Open the language folder.
3. Print the PDF. Every page already has {SITE} and the maker line.

Folders
A–Z     Languages by English name
#       Names that do not start with A–Z
Chapter samples     Genesis 1, John 3, Matthew 5

These files are 6×9 inches, made for print. Scripture copyright stays with each translation’s publishers and is printed on the cover.
"""
    (dest / "Read Me.txt").write_text(text, encoding="utf-8")


def organize(dest: Path, source: Path | None = None) -> dict:
    source = source or PDF_DIR
    rows = load_catalog()
    dest.mkdir(parents=True, exist_ok=True)
    used_by_lang: dict[str, set[str]] = {}
    placed = 0
    missing = []
    index_rows = []
    for row in rows:
        language = safe_name(row.get("language") or "Unknown", "Unknown")
        bucket = letter_bucket(language)
        used = used_by_lang.setdefault(language, set())
        filename = pdf_filename(row, used)
        src = source / f"ChristSupplyHolyBible-{row['id']}.pdf"
        if not src.exists():
            missing.append(row["id"])
            continue
        target = dest / bucket / language / filename
        place(src, target)
        placed += 1
        index_rows.append(
            {
                "letter": bucket,
                "language": language,
                "coverage": coverage_label(row),
                "title": row.get("title") or row["id"],
                "id": row["id"],
                "file": str(Path(bucket) / language / filename),
            }
        )

    sample_dir = dest / "Chapter samples"
    for sample in sorted(SAMPLE_DIR.glob("ChristSupply.Net-*.pdf")):
        place(sample, sample_dir / sample.name)

    languages = len({row["language"] for row in index_rows})
    write_readme(dest, placed, languages)
    with (dest / "Index of 1300 translations.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["letter", "language", "coverage", "title", "id", "file"])
        writer.writeheader()
        writer.writerows(sorted(index_rows, key=lambda r: (r["letter"], r["language"].casefold(), r["title"])))
    return {"placed": placed, "missing": missing, "languages": languages, "dest": str(dest)}


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Copy {BRAND} PDFs into Desktop language folders")
    parser.add_argument("--dest", default="", help="Destination folder (default: ~/Desktop/Christ Supply Holy Bible)")
    parser.add_argument("--source", default=str(PDF_DIR))
    parser.add_argument("--clean", action="store_true", help="Remove the destination folder first")
    args = parser.parse_args()
    dest = Path(args.dest).expanduser() if args.dest else default_desktop()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if args.clean and dest.exists():
        shutil.rmtree(dest)
    result = organize(dest, Path(args.source))
    print(f"placed {result['placed']} PDFs in {result['languages']} language folders")
    print(result["dest"])
    if result["missing"]:
        print(f"missing {len(result['missing'])}: " + ", ".join(result["missing"][:20]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
