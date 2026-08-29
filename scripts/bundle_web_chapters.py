#!/usr/bin/env python3
"""Download the public-domain World English Bible and write the iOS chapter bundle.

Source: https://api.getbible.net/v2/web.json (eBible WEB / engwebp).
Output: ios/ChristSupplyMatrix/Resources/web-chapters.json
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "ChristSupplyMatrix" / "Resources" / "web-chapters.json"
URL = "https://api.getbible.net/v2/web.json"


def compact(data: dict) -> dict:
    chapters: dict[str, list[list]] = {}
    count = 0
    for book in data.get("books") or []:
        book_n = int(book.get("nr") or 0)
        for chapter in book.get("chapters") or []:
            chapter_n = int(chapter.get("chapter") or chapter.get("nr") or 0)
            verses: list[list] = []
            for row in chapter.get("verses") or []:
                verse_n = int(row.get("verse") or 0)
                text = str(row.get("text") or "").strip()
                if verse_n and text:
                    verses.append([verse_n, text])
                    count += 1
            if verses:
                chapters[f"{book_n}:{chapter_n}"] = verses
    return {
        "id": "web",
        "ebibleId": "engwebp",
        "title": "World English Bible",
        "copyright": "public domain",
        "verseCount": count,
        "chapterCount": len(chapters),
        "chapters": chapters,
    }


def main() -> None:
    print(f"fetch {URL}")
    with urllib.request.urlopen(URL, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    bundle = compact(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
    print(f"verses {bundle['verseCount']:,} chapters {bundle['chapterCount']}")


if __name__ == "__main__":
    main()
