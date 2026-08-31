#!/usr/bin/env python3
"""Validate the iPhone Matrix app project, indexes, and bundled WEB text."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IOS = ROOT / "ios"
APP = IOS / "ChristSupplyMatrix"
PBX = IOS / "ChristSupplyMatrix.xcodeproj" / "project.pbxproj"
SWIFT_FILES = [
    "ChristSupplyMatrixApp.swift",
    "MatrixTheme.swift",
    "IndexModels.swift",
    "CatalogStore.swift",
    "ScriptureStore.swift",
    "ChromeViews.swift",
    "IndexViews.swift",
    "ReaderView.swift",
]
BRAND = {
    "name": "Christ Supply Holy Bible",
    "site": "ChristSupply.Net",
    "credit": "Made by Liberated Luis With Cursor, Claude Opus, and MacBook",
    "equal": "All Users Are Created Equally By God",
    "liberate": "LIBERA OMNES UTENTES | LIBERATE ALL USERS",
}
RAINBOW = ["red", "orange", "gold", "yellow", "green", "cyan", "blue", "purple", "pink"]
THEMES = ["lord-said", "afraid", "mercy", "believe", "love", "peace", "sin", "wrath"]


def load_indexes() -> dict:
    return json.loads((ROOT / "data" / "indexes.json").read_text(encoding="utf-8"))


def load_books() -> list[dict]:
    return json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))


def load_web() -> dict:
    return json.loads((APP / "Resources" / "web-chapters.json").read_text(encoding="utf-8"))


def swift_blob() -> str:
    return "\n".join((APP / name).read_text(encoding="utf-8") for name in SWIFT_FILES)


class IOSProjectTests(unittest.TestCase):
    def test_xcode_project_is_complete(self):
        self.assertTrue(PBX.is_file(), "missing .xcodeproj")
        pbx = PBX.read_text(encoding="utf-8")
        self.assertTrue(pbx.startswith("// !$*UTF8*$!"))
        self.assertIn("rootObject = AA0000000000000000000081", pbx)
        self.assertIn("com.apple.product-type.application", pbx)
        self.assertIn("TARGETED_DEVICE_FAMILY = 1", pbx)
        self.assertIn("IPHONEOS_DEPLOYMENT_TARGET = 17.0", pbx)
        self.assertIn("net.christsupply.holybible", pbx)
        self.assertIn("SDKROOT = iphoneos", pbx)
        for name in SWIFT_FILES:
            self.assertIn(name, pbx)
            self.assertTrue((APP / name).is_file(), name)
        self.assertIn("indexes.json", pbx)
        self.assertIn("books.json", pbx)
        self.assertIn("web-chapters.json", pbx)
        self.assertIn("../data/indexes.json", pbx)
        self.assertIn("../data/books.json", pbx)
        self.assertTrue((ROOT / "data" / "indexes.json").is_file())
        self.assertTrue((ROOT / "data" / "books.json").is_file())
        self.assertTrue((APP / "Info.plist").is_file())
        self.assertTrue((APP / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png").is_file())
        self.assertTrue((IOS / "README.md").is_file())
        self.assertTrue((IOS / "ChristSupplyMatrix.xcodeproj" / "xcshareddata" / "xcschemes" / "ChristSupplyMatrix.xcscheme").is_file())

    def test_iphone_not_ipad_only(self):
        pbx = PBX.read_text(encoding="utf-8")
        self.assertIn("TARGETED_DEVICE_FAMILY = 1;", pbx)
        self.assertNotIn("TARGETED_DEVICE_FAMILY = 2", pbx)
        info = (APP / "Info.plist").read_text(encoding="utf-8")
        self.assertIn("UIInterfaceOrientationPortrait", info)

    def test_brand_strings_are_exact(self):
        blob = swift_blob() + (IOS / "README.md").read_text(encoding="utf-8")
        for value in BRAND.values():
            self.assertIn(value, blob)
        app = (APP / "ChristSupplyMatrixApp.swift").read_text(encoding="utf-8")
        self.assertIn("IndexPageView", app)
        self.assertIn("ReaderView", app)
        theme = (APP / "MatrixTheme.swift").read_text(encoding="utf-8")
        for color in RAINBOW:
            self.assertIn(f'"{color}"', theme)
        for theme_id in THEMES:
            self.assertIn(f'"{theme_id}"', theme)


class IndexAndScriptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indexes = load_indexes()
        cls.books = {row["id"]: row for row in load_books()}
        cls.web = load_web()

    def test_index_families_present(self):
        data = self.indexes
        self.assertEqual(data["brand"], BRAND["name"])
        self.assertEqual(data["site"], BRAND["site"])
        self.assertEqual(data["credit"], BRAND["credit"])
        self.assertEqual(data["equal"], BRAND["equal"])
        self.assertEqual(data["liberate"], BRAND["liberate"])
        self.assertEqual(list(data["rainbow"]), RAINBOW)
        self.assertEqual(list(data["themes"]), THEMES)
        self.assertGreaterEqual(len(data["iam"]), 100)
        self.assertEqual(len(data["arcs"]), 500)
        self.assertEqual(len(data["help"]), 8)
        self.assertGreaterEqual(len(data["women"]), 10)
        self.assertGreaterEqual(len(data["men"]), 10)
        self.assertEqual(len(data["roots"]), 66)
        self.assertGreaterEqual(len(data["dictionary"]), 900)
        ids = {row["id"] for row in data["wordOfGod"]["entries"]}
        self.assertEqual(ids, {"genesis", "john", "library"})

    def test_web_bundle_covers_index_chapters(self):
        chapters = self.web["chapters"]
        self.assertGreaterEqual(self.web["verseCount"], 31000)
        self.assertGreaterEqual(self.web["chapterCount"], 1180)
        self.assertEqual(self.web["ebibleId"], "engwebp")
        self.assertEqual(chapters["1:1"][0][1][:16].lower(), "in the beginning")
        self.assertIn("the Word was God", chapters["43:1"][0][1])

        missing: list[str] = []
        checked = 0

        def need(book: int, chapter: int) -> None:
            nonlocal checked
            checked += 1
            if f"{book}:{chapter}" not in chapters:
                missing.append(f"{book}:{chapter}")

        for family in list(self.indexes["rainbow"].values()) + list(self.indexes["themes"].values()):
            for book, rows in family["versesByBook"].items():
                for chapter, _verse in rows:
                    need(int(book), int(chapter))
        for key in ("iam", "arcs", "help", "women", "men", "roots", "dictionary"):
            for row in self.indexes[key]:
                for book, chapter, _verse in row.get("verses") or []:
                    need(int(book), int(chapter))
        for entry in self.indexes["wordOfGod"]["entries"]:
            if entry.get("book") and entry.get("chapter"):
                need(int(entry["book"]), int(entry["chapter"]))

        self.assertGreater(checked, 5000)
        self.assertEqual(missing[:20], [], f"{len(missing)} index chapters missing from WEB bundle")

    def test_sample_navigation_reaches_web_text(self):
        """Root Index → rainbow/theme → verse → WEB text, same as the iPhone stack."""
        red = self.indexes["rainbow"]["red"]
        self.assertIn("40", red["versesByBook"])
        matthew = red["versesByBook"]["40"][0]
        chapter, verse = matthew
        lines = {n: text for n, text in self.web["chapters"]["40:" + str(chapter)]}
        self.assertIn(verse, lines)
        self.assertGreater(len(lines[verse]), 8)

        afraid = self.indexes["themes"]["afraid"]
        book_id, rows = next(iter(afraid["versesByBook"].items()))
        chapter, verse = rows[0]
        key = f"{book_id}:{chapter}"
        self.assertIn(key, self.web["chapters"])
        self.assertTrue(any(n == verse for n, _t in self.web["chapters"][key]))

        john = next(row for row in self.indexes["wordOfGod"]["entries"] if row["id"] == "john")
        text = self.web["chapters"][f"{john['book']}:{john['chapter']}"][0][1]
        self.assertIn("Word", text)

        help_row = self.indexes["help"][0]
        book, chapter, verse = help_row["verses"][0]
        self.assertTrue(any(n == verse for n, _t in self.web["chapters"][f"{book}:{chapter}"]))

    def test_swift_implements_root_to_reader(self):
        index_views = (APP / "IndexViews.swift").read_text(encoding="utf-8")
        reader = (APP / "ReaderView.swift").read_text(encoding="utf-8")
        store = (APP / "ScriptureStore.swift").read_text(encoding="utf-8")
        self.assertIn("RootIndexView", index_views)
        self.assertIn("PackedIndexView", index_views)
        self.assertIn("openPassage", index_views)
        self.assertIn('open(["word"])', index_views)
        self.assertIn("web-chapters", store)
        self.assertIn("api.getbible.net/v2/web", store)
        self.assertIn("highlight", reader)
        self.assertIn("World English Bible", (APP / "MatrixTheme.swift").read_text(encoding="utf-8"))

    def test_pbx_ids_are_24_hex(self):
        ids = re.findall(r"\b([A-F0-9]{24})\b", PBX.read_text(encoding="utf-8"))
        self.assertGreater(len(set(ids)), 20)
        self.assertTrue(all(len(item) == 24 for item in ids))


if __name__ == "__main__":
    unittest.main()
