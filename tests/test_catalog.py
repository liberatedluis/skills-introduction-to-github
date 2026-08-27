#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from languages_seed import parse_seed  # noqa: E402


class CatalogTests(unittest.TestCase):
    def test_seed_is_300_unique(self):
        rows = parse_seed()
        self.assertEqual(len(rows), 300)
        self.assertEqual(len({row["iso"] for row in rows}), 300)
        self.assertEqual(rows[0]["iso"], "eng")
        self.assertEqual(rows[-1]["iso"], "epo")

    def test_languages_json(self):
        payload = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["brand"], "Christ Supply Bible")
        self.assertEqual(payload["credit"], "built by Cursor with Liberated")
        self.assertEqual(payload["site"], "ChristSupply.Net")
        self.assertEqual(payload["count"], 300)
        self.assertEqual(len(payload["languages"]), 300)
        self.assertTrue(payload["withText"] > 100)
        self.assertTrue(all(lang["siteMark"] == "ChristSupply.Net" for lang in payload["languages"]))

    def test_every_surface_marks_christsupply(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "assets" / "css" / "app.css").read_text(encoding="utf-8")
        js = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("ChristSupply.Net", html)
        self.assertIn('class="print-running top"', html)
        self.assertIn('class="print-running bottom"', html)
        self.assertIn("print-running", css)
        self.assertIn('const SITE = "ChristSupply.Net"', js)
        self.assertIn("pageMark", js)
        self.assertIn("txtBanner", js)

    def test_books_complete(self):
        books = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
        self.assertEqual(len(books), 66)
        self.assertEqual(books[0]["usfm"], "GEN")
        self.assertEqual(books[-1]["usfm"], "REV")


if __name__ == "__main__":
    unittest.main()
