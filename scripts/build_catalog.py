#!/usr/bin/env python3
"""Build data/languages.json for Christ Supply Bible."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from languages_seed import ALIASES, parse_seed  # noqa: E402

EBIBLE_CSV = ROOT / "data" / "ebible-translations.csv"
OUT = ROOT / "data" / "languages.json"

BOLL_BY_ISO = {
    "eng": {"id": "WEB", "name": "World English Bible"},
    "spa": {"id": "RV2004", "name": "Reina Valera Gómez 2004"},
    "fra": {"id": "FRLSG", "name": "Bible Segond 1910"},
    "deu": {"id": "LUT", "name": "Luther 1912"},
    "rus": {"id": "SYNOD", "name": "Синодальный перевод"},
    "ukr": {"id": "UKRK", "name": "Куліш / Нечуй-Левицький / Пулюй 1903"},
    "por": {"id": "TB10", "name": "Tradução Brasileira 2010"},
    "nld": {"id": "DSV", "name": "Statenvertaling 1619"},
    "cmn": {"id": "PCBS", "name": "Peking Committee Bible 1899"},
    "yue": {"id": "CUV", "name": "Chinese Union Traditional"},
    "hin": {"id": "HIOV", "name": "Hindi O.V."},
    "ind": {"id": "TB", "name": "Terjemahan Baru"},
    "jpn": {"id": "JPKJV", "name": "口語訳聖書 1954/1955"},
    "kor": {"id": "KRV", "name": "개역한글"},
    "vie": {"id": "VI1934", "name": "Kinh Thánh 1934"},
    "swh": {"id": "SUV", "name": "Swahili Union Version 1997"},
    "tam": {"id": "TAMOVR", "name": "Tamil O.V."},
    "arb": {"id": "SVD", "name": "Smith and Van Dyke", "rtl": True},
    "ara": {"id": "SVD", "name": "Smith and Van Dyke", "rtl": True},
    "pes": {"id": "POV", "name": "Persian Old Version", "rtl": True},
    "heb": {"id": "WLC", "name": "Westminster Leningrad Codex", "rtl": True},
    "hbo": {"id": "WLC", "name": "Westminster Leningrad Codex", "rtl": True},
    "ell": {"id": "LXX", "name": "Septuagint"},
    "grc": {"id": "LXX", "name": "Septuagint"},
    "lat": {"id": "VULG", "name": "Clementine Vulgate"},
    "ita": {"id": "NR06", "name": "Nuova Riveduta 2006"},
    "pol": {"id": "BG", "name": "Biblia Gdańska 1881"},
    "ron": {"id": "VDCL", "name": "Cornilescu 1931"},
    "hun": {"id": "KB", "name": "Károli 1908"},
    "ces": {"id": "CSP09", "name": "Český studijní překlad"},
    "afr": {"id": "AFR53", "name": "Afrikaans 1933/1953"},
    "nor": {"id": "DNB", "name": "Det Norske Bibelselskap 1930"},
    "nob": {"id": "DNB", "name": "Det Norske Bibelselskap 1930"},
    "swe": {"id": "SFB2015", "name": "Svenska Folkbibeln 2015"},
    "kan": {"id": "KNCL", "name": "Kannada C.L."},
    "mal": {"id": "MOV", "name": "Malayalam O.V."},
    "npi": {"id": "NNRV", "name": "Nepali New Revised Version"},
    "chu": {"id": "CSL", "name": "Church Slavonic 1900"},
}

GETBIBLE_LANG_TO_ISO = {
    "english": "eng",
    "chinese": "cmn",
    "german": "deu",
    "japanese": "jpn",
    "greek": "grc",
    "hebrew": "hbo",
    "portuguese": "por",
    "dutch": "nld",
    "danish": "dan",
    "french": "fra",
    "finnish": "fin",
    "spanish": "spa",
    "swedish": "swe",
    "czech": "ces",
    "myanmar burmse": "mya",
    "coptic": "cop",
    "armenian": "hye",
    "italian": "ita",
    "korean": "kor",
    "polish": "pol",
    "serbian": "srp",
    "russian": "rus",
    "turkish": "tur",
    "ukrainian": "ukr",
    "albanian": "als",
    "afrikaans": "afr",
    "arabic": "arb",
    "basque": "eus",
    "norwegian bokmal": "nob",
    "breton": "bre",
    "chamorro": "cha",
    "romanian": "ron",
    "croatian": "hrv",
    "slavonic elizabeth": "chu",
    "dari": "prs",
    "esperanto": "epo",
    "estonian": "ekk",
    "scottish gaelic": "gla",
    "hungarian": "hun",
    "latvian": "lav",
    "lithuanian": "lit",
    "manx gaelic": "glv",
    "maori": "mri",
    "malagasy": "mlg",
    "greek modern": "ell",
    "mongolian": "khk",
    "ndebele": "nbl",
    "norwegian nynorsk": "nno",
    "syriac": "syc",
    "shona": "sna",
    "swahili": "swh",
    "tagalog": "tgl",
    "tausug": "tsg",
    "thai": "tha",
    "vietnamese": "vie",
    "latin": "lat",
    "pohnpeian": "pon",
}

PREFERRED_EBIBLE = {
    "eng": "engwebp",
    "spa": "spaRV1909",
    "fra": "frasbl",
    "deu": "deuelo",
    "hin": "hin2017",
    "ben": "ben2017",
    "por": "porbrbsl",
    "ind": "indags",
    "urd": "urd",
    "rus": "russyn",
    "cmn": "cmnswcb",
    "tgl": "tglulb",
    "fil": "tglulb",
}

PREFERRED_GETBIBLE = {
    "eng": "kjv",
    "cmn": "cus",
    "deu": "luther1545",
    "jpn": "japkougo",
    "grc": "lxx",
    "hbo": "codex",
    "por": "almeida",
    "nld": "statenvertaling",
    "dan": "danish",
    "fra": "ls1910",
    "fin": "finnish1776",
    "spa": "valera",
    "swe": "swedish",
    "ces": "bkr",
    "mya": "judson",
    "cop": "coptic",
    "hye": "westernarmenian",
    "ita": "giovanni",
    "kor": "korean",
    "pol": "polgdanska",
    "srp": "srkdekavski",
    "rus": "synodal",
    "tur": "turkish",
    "ukr": "ukrogienko",
    "als": "alb",
    "afr": "aov",
    "arb": "arabicsv",
    "eus": "basque",
    "nob": "norwegian",
    "bre": "breton",
    "cha": "chamorro",
    "ron": "cornilescu",
    "hrv": "croatia",
    "chu": "churchslavonic",
    "prs": "dari",
    "epo": "esperanto",
    "ekk": "estonian",
    "gla": "gaelic",
    "hun": "karoli",
    "lav": "latvian",
    "lit": "lithuanian",
    "mri": "maori",
    "ell": "modern-greek",
    "khk": "mongolian",
    "sna": "shona",
    "swh": "swahili",
    "tgl": "tagalog",
    "tha": "thai",
    "vie": "vietnamese",
    "lat": "vulgate",
    "pon": "pohnpeian",
}


def codes_for(iso: str) -> list[str]:
    codes = [iso]
    codes.extend(ALIASES.get(iso, []))
    out = []
    seen = set()
    for c in codes:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def load_ebible() -> dict[str, list[dict]]:
    by_lang: dict[str, list[dict]] = {}
    with EBIBLE_CSV.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            lang = (row.get("languageCode") or "").strip()
            if not lang:
                continue
            rec = {
                "id": row["translationId"],
                "title": row.get("title") or row.get("shortTitle") or row["translationId"],
                "copyright": row.get("Copyright") or "",
                "redistributable": row.get("Redistributable") == "True",
                "downloadable": row.get("downloadable") == "True",
                "otBooks": int(row.get("OTbooks") or 0),
                "ntBooks": int(row.get("NTbooks") or 0),
                "otVerses": int(row.get("OTverses") or 0),
                "ntVerses": int(row.get("NTverses") or 0),
                "dir": "rtl" if (row.get("textDirection") or "").lower() == "rtl" else "ltr",
                "script": row.get("script") or "",
            }
            by_lang.setdefault(lang.lower(), []).append(rec)
    return by_lang


def score_translation(t: dict) -> tuple:
    verses = t["otVerses"] + t["ntVerses"]
    full = 1 if t["otBooks"] >= 39 and t["ntBooks"] >= 27 else 0
    nt = 1 if t["ntBooks"] >= 27 else 0
    free = 1 if t["redistributable"] and t["downloadable"] else 0
    return (free, full, nt, verses)


def pick_ebible(iso: str, by_lang: dict[str, list[dict]]) -> dict | None:
    candidates: list[dict] = []
    wanted = {c.lower() for c in codes_for(iso)}
    for code, rows in by_lang.items():
        if code in wanted or any(code.startswith(c) for c in wanted if len(c) >= 3):
            candidates.extend(rows)
            continue
        for row in rows:
            rid = row["id"].lower()
            if any(rid.startswith(c) for c in wanted if len(c) >= 3):
                candidates.append(row)
    if not candidates:
        return None
    preferred = PREFERRED_EBIBLE.get(iso)
    if preferred:
        for row in candidates:
            if row["id"] == preferred:
                return row
    free = [t for t in candidates if t["redistributable"] and t["downloadable"]]
    pool = free or candidates
    pool.sort(key=score_translation, reverse=True)
    return pool[0]


def coverage(t: dict | None) -> str:
    if not t:
        return "none"
    if t["otBooks"] >= 39 and t["ntBooks"] >= 27:
        return "bible"
    if t["ntBooks"] >= 27:
        return "nt"
    if t["otBooks"] + t["ntBooks"] > 0:
        return "portions"
    return "none"


def main() -> None:
    seed = parse_seed()
    if len(seed) != 300:
        raise SystemExit(f"expected 300 unique languages, got {len(seed)}")
    ebible = load_ebible()
    languages = []
    with_text = 0
    for row in seed:
        iso = row["iso"]
        eb = pick_ebible(iso, ebible)
        sources = []
        if iso in BOLL_BY_ISO:
            b = BOLL_BY_ISO[iso]
            sources.append(
                {
                    "kind": "bolls",
                    "id": b["id"],
                    "name": b["name"],
                }
            )
        gb = PREFERRED_GETBIBLE.get(iso)
        if gb:
            sources.append({"kind": "getbible", "id": gb, "name": gb})
        if eb:
            sources.append(
                {
                    "kind": "ebible",
                    "id": eb["id"],
                    "name": eb["title"],
                    "copyright": eb["copyright"],
                    "otBooks": eb["otBooks"],
                    "ntBooks": eb["ntBooks"],
                }
            )
        cov = coverage(eb)
        if sources:
            with_text += 1
            if cov == "none":
                cov = "available"
        languages.append(
            {
                "rank": row["rank"],
                "iso": iso,
                "name": row["name"],
                "native": row["native"],
                "speakersM": row["speakersM"],
                "script": row["script"],
                "rtl": row["rtl"] or (eb["dir"] == "rtl" if eb else False),
                "region": row["region"],
                "coverage": cov,
                "sources": sources,
                "siteMark": "ChristSupply.Net",
            }
        )
    payload = {
        "brand": "Christ Supply Bible",
        "credit": "built by Cursor with Liberated",
        "site": "ChristSupply.Net",
        "siteUrl": "https://christsupply.net",
        "count": len(languages),
        "withText": with_text,
        "languages": languages,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(languages)} languages, {with_text} with a live source)")


if __name__ == "__main__":
    main()
