#!/usr/bin/env python3
"""1,300 open Christ Supply Holy Bible translations for print PDFs and the Matrix reader."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import BRAND, CREDIT, SITE, SITE_URL  # noqa: E402
from copy_holy_bibles_to_desktop import letter_bucket, pdf_filename, safe_name  # noqa: E402

CSV_PATH = ROOT / "data" / "ebible-translations.csv"
READER_CATALOG = ROOT / "data" / "translations.json"
PRINT_CATALOG = ROOT / "pdfs" / "holy-bibles" / "catalog.json"

GETBIBLE_EXTRAS = [
    {
        "id": "che1860",
        "title": "Cherokee New Testament 1860",
        "language": "Cherokee",
        "script": "Cherokee",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 27,
        "coverage": "nt",
    },
    {
        "id": "gothic",
        "title": "Gothic Bible portions",
        "language": "Gothic",
        "script": "Gothic",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 0,
        "coverage": "portions",
    },
    {
        "id": "sahidic",
        "title": "Sahidic Coptic New Testament",
        "language": "Coptic",
        "script": "Coptic",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 27,
        "coverage": "nt",
    },
    {
        "id": "manxgaelic",
        "title": "Manx Gaelic Bible portions",
        "language": "Manx Gaelic",
        "script": "Latin",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 0,
        "coverage": "portions",
    },
    {
        "id": "potawatomi",
        "title": "Potawatomi Matthew and Acts 1844",
        "language": "Potawatomi",
        "script": "Latin",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 0,
        "coverage": "portions",
    },
    {
        "id": "calo",
        "title": "Caló Gospel of Luke",
        "language": "Caló",
        "script": "Latin",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 0,
        "coverage": "portions",
    },
    {
        "id": "gaelic",
        "title": "Scots Gaelic Gospel of Mark",
        "language": "Scottish Gaelic",
        "script": "Latin",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 0,
        "coverage": "portions",
    },
    {
        "id": "peshitta",
        "title": "Syriac Peshitta New Testament",
        "language": "Syriac",
        "script": "Syriac",
        "rtl": True,
        "otBooks": 0,
        "ntBooks": 27,
        "coverage": "nt",
    },
    {
        "id": "basque",
        "title": "Basque Navarro-Labourdin New Testament",
        "language": "Basque",
        "script": "Latin",
        "rtl": False,
        "otBooks": 0,
        "ntBooks": 27,
        "coverage": "nt",
    },
]


def verses_of(row: dict) -> int:
    def n(key: str) -> int:
        try:
            return int(row.get(key) or 0)
        except ValueError:
            return 0

    return n("OTverses") + n("NTverses") + n("DCverses")


def int_of(row: dict, key: str) -> int:
    try:
        return int(row.get(key) or 0)
    except ValueError:
        return 0


def coverage_of(row: dict) -> str:
    ot, nt = int_of(row, "OTbooks"), int_of(row, "NTbooks")
    if ot >= 39 and nt >= 27:
        return "bible"
    if nt >= 27:
        return "nt"
    return "portions"


def attach_print_paths(catalog: list[dict]) -> list[dict]:
    used_by_lang: dict[str, set[str]] = {}
    for row in catalog:
        language = safe_name(row.get("language") or "Unknown", "Unknown")
        used = used_by_lang.setdefault(language, set())
        filename = pdf_filename(row, used)
        bucket = letter_bucket(language)
        row["printPath"] = f"{bucket}/{language}/{filename}"
        row["siteMark"] = SITE
    return catalog


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
                "otBooks": int_of(row, "OTbooks"),
                "ntBooks": int_of(row, "NTbooks"),
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
                "verses": extra.get("verses") or 0,
                "coverage": extra.get("coverage") or "portions",
                "otBooks": extra.get("otBooks") or 0,
                "ntBooks": extra.get("ntBooks") or 0,
            }
        )
        if len(catalog) >= 1300:
            break
    if len(catalog) > 1300:
        catalog = catalog[:1300]
    if len(catalog) < 1300:
        raise SystemExit(f"only {len(catalog)} open translations available")
    return attach_print_paths(catalog)


def catalog_payload(catalog: list[dict]) -> dict:
    return {
        "brand": BRAND,
        "credit": CREDIT,
        "site": SITE,
        "siteUrl": SITE_URL,
        "count": len(catalog),
        "translations": catalog,
    }


def write_reader_catalog(catalog: list[dict] | None = None) -> Path:
    catalog = catalog or build_catalog()
    payload = catalog_payload(catalog)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    READER_CATALOG.parent.mkdir(parents=True, exist_ok=True)
    READER_CATALOG.write_text(text, encoding="utf-8")
    PRINT_CATALOG.parent.mkdir(parents=True, exist_ok=True)
    PRINT_CATALOG.write_text(text, encoding="utf-8")
    return READER_CATALOG


def main() -> None:
    path = write_reader_catalog()
    print(f"wrote {path} (1,300 Matrix-scrollable translations) · {SITE}")


if __name__ == "__main__":
    main()
