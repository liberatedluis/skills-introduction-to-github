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
        self.assertEqual(payload["brand"], "Christ Supply Holy Bible")
        self.assertEqual(payload["credit"], "Made by Liberated Luis With Cursor, Claude Opus, and MacBook")
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
        self.assertIn("Christ Supply Holy Bible", html)
        self.assertIn("Made by Liberated Luis With Cursor, Claude Opus, and MacBook", html)
        self.assertIn('const BRAND = "Christ Supply Holy Bible"', js)

    def test_sample_pdfs_exist(self):
        pdf_dir = ROOT / "pdfs"
        names = [
            "ChristSupply.Net-English-Genesis-1.pdf",
            "ChristSupply.Net-English-John-3.pdf",
            "ChristSupply.Net-English-Matthew-5.pdf",
            "ChristSupply.Net-Spanish-Genesis-1.pdf",
        ]
        for name in names:
            path = pdf_dir / name
            self.assertTrue(path.exists(), name)
            self.assertGreater(path.stat().st_size, 1000, name)

        books = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
        self.assertEqual(len(books), 66)
        self.assertEqual(books[0]["usfm"], "GEN")
        self.assertEqual(books[-1]["usfm"], "REV")

    def test_1300_print_catalog(self):
        from holy_catalog import build_catalog

        catalog = build_catalog()
        self.assertEqual(len(catalog), 1300)
        self.assertEqual(len({row["id"] for row in catalog}), 1300)
        self.assertTrue(any(row["id"] == "engwebp" for row in catalog))
        self.assertTrue(all("otBooks" in row and "ntBooks" in row for row in catalog))
        self.assertTrue(all(row.get("printPath") for row in catalog))
        self.assertTrue(all(row.get("siteMark") == "ChristSupply.Net" for row in catalog))

    def test_1300_scroll_catalog(self):
        payload = json.loads((ROOT / "data" / "translations.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["brand"], "Christ Supply Holy Bible")
        self.assertEqual(payload["site"], "ChristSupply.Net")
        self.assertEqual(payload["count"], 1300)
        self.assertEqual(len(payload["translations"]), 1300)
        self.assertEqual(len({row["id"] for row in payload["translations"]}), 1300)
        self.assertTrue(any(row["id"] in {"engwebp", "eng-web", "engwebu"} for row in payload["translations"]))
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")
        print_html = (ROOT / "print.html").read_text(encoding="utf-8")
        self.assertIn("1,300", html)
        self.assertIn("Search 1,300 Matrix Holy Bibles", html)
        self.assertIn("hashchange", js)
        self.assertIn("data/translations.json", js)
        self.assertIn("scroll-more", js)
        self.assertIn("printCatalog", print_html)
        self.assertIn("1,300", print_html)
        self.assertIn("offline-app.html", html)
        self.assertIn("offline-app.html", print_html)

    def test_clickable_web_indexes(self):
        payload = json.loads((ROOT / "data" / "indexes.json").read_text(encoding="utf-8"))
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")
        idx = (ROOT / "assets" / "js" / "indexes.js").read_text(encoding="utf-8")
        self.assertEqual(payload["site"], "ChristSupply.Net")
        self.assertEqual(payload["brand"], "Christ Supply Holy Bible")
        for color in ("red", "orange", "gold", "yellow", "green", "cyan", "blue", "purple", "pink"):
            self.assertIn(color, payload["rainbow"])
            self.assertGreater(payload["rainbow"][color]["count"], 0)
            self.assertTrue(payload["rainbow"][color]["versesByBook"])
        self.assertGreaterEqual(payload["rainbow"]["red"]["count"], 2000)
        self.assertTrue(payload["rainbow"]["red"]["versesByBook"]["40"])
        self.assertEqual(payload["rainbow"]["red"]["versesByBook"]["40"][0][0], 3)
        for theme in ("lord-said", "afraid", "mercy", "believe", "love", "peace", "sin", "wrath"):
            self.assertIn(theme, payload["themes"])
            self.assertGreater(payload["themes"][theme]["count"], 0)
        self.assertEqual(len(payload["iam"]), 116)
        self.assertTrue(any(row["id"] == "iam-the-way-the-truth-and-the-life" for row in payload["iam"]))
        self.assertEqual(len(payload["arcs"]), 500)
        self.assertEqual(payload["arcs"][0]["verses"][0], [43, 3, 16])
        self.assertEqual(len(payload["women"]), 18)
        self.assertEqual(payload["women"][0]["title"], "Sarah")
        self.assertEqual(len(payload["men"]), 20)
        self.assertGreaterEqual(len(payload["dictionary"]), 900)
        self.assertEqual(payload["dictionary"][0]["word"], "Aaron")
        self.assertEqual(len(payload["roots"]), 66)
        self.assertEqual(len(payload["help"]), 8)
        self.assertIn('value="index"', html)
        self.assertIn('id="indexBtn"', html)
        self.assertIn("view-index", html)
        self.assertIn("loadIndexes", js)
        self.assertIn("openIndex", js)
        self.assertIn("Root Index", idx)
        self.assertIn("I AM THE LORD", idx)

    def test_getbible_list_of_books_parses(self):
        from make_holy_bible_pdfs import _getbible_book_iter, load_getbible_verses

        sample = {
            "translation": "Cherokee New Testament",
            "books": [
                {
                    "nr": 40,
                    "name": "Matthew",
                    "chapters": [
                        {
                            "chapter": 1,
                            "verses": [{"chapter": 1, "verse": 1, "text": "ᎾᏍᎩ"}],
                        }
                    ],
                }
            ],
        }
        books = _getbible_book_iter(sample)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["nr"], 40)

        import make_holy_bible_pdfs as pdfs

        pdfs.fetch = lambda url: json.dumps(sample).encode("utf-8")
        verses = load_getbible_verses("che1860")
        self.assertEqual(verses[0][0], "MAT")
        self.assertEqual(verses[0][3], "ᎾᏍᎩ")

    def test_script_fonts_cover_print_scripts(self):
        from make_holy_bible_pdfs import detect_script, font_for, normalize_script

        self.assertEqual(detect_script("בראשית ברא אלהים"), "Hebrew")
        self.assertEqual(detect_script("فِي الْبَدْءِ"), "Arabic")
        self.assertEqual(detect_script("आरम्भ में"), "Devanagari")
        self.assertEqual(detect_script("ⴰⴷⵔⴰⵔ"), "Tifinagh")
        self.assertEqual(normalize_script("Tifenagh"), "Tifinagh")
        self.assertEqual(normalize_script("Amheric"), "Ethiopic")
        self.assertEqual(normalize_script("Burmese"), "Myanmar")
        for script in ("Latin", "Hebrew", "Arabic", "Devanagari", "Tifinagh", "Myanmar", "Thai", "CJK"):
            path = font_for(script)
            self.assertTrue(path.exists(), f"{script} -> {path}")

    def test_desktop_folder_names(self):
        from copy_holy_bibles_to_desktop import letter_bucket, pdf_filename, safe_name

        self.assertEqual(safe_name('English / WEB'), "English WEB")
        self.assertEqual(letter_bucket("English"), "E")
        self.assertEqual(letter_bucket("Spanish"), "S")
        self.assertEqual(letter_bucket("Hebrew"), "H")
        used = set()
        first = pdf_filename({"id": "engwebp", "title": "World English Bible", "coverage": "bible"}, used)
        second = pdf_filename({"id": "eng-web", "title": "World English Bible", "coverage": "bible"}, used)
        self.assertTrue(first.endswith(".pdf"))
        self.assertIn("Full Bible", first)
        self.assertIn("eng-web", second)

    def test_constitutional_offline_app_pdf(self):
        from make_constitutional_pdf import PAGE_H, PAGE_W, build_constitutional_pdf

        dest = Path("/tmp/constitutional-sample-clickable-pages.pdf")
        verses = [
            ("GEN", 1, 1, "In the beginning, God created the heavens and the earth."),
            ("GEN", 1, 2, "The earth was formless and empty. God's Spirit was hovering over the waters."),
            ("GEN", 1, 3, "God said, Let there be light, and there was light."),
            ("JHN", 1, 1, "In the beginning was the Word, and the Word was with God, and the Word was God."),
            ("JHN", 1, 14, "The Word became flesh and lived among us. Jesus Christ."),
        ]
        path = build_constitutional_pdf(verses, dest)
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 5000)

        html = (ROOT / "offline-app.html").read_text(encoding="utf-8")
        css = (ROOT / "assets" / "css" / "constitutional.css").read_text(encoding="utf-8")
        js = (ROOT / "assets" / "js" / "constitutional.js").read_text(encoding="utf-8")
        self.assertIn("All Users Are Created Equally By", html)
        self.assertIn("LIBERA OMNES UTENTES", html)
        self.assertIn("ChristSupply.Net", html)
        self.assertIn("offline-app.html", (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertIn("constitutional dark", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("--god", css)
        self.assertIn("engwebp", js)

        import pymupdf

        doc = pymupdf.open(str(path))
        self.assertGreaterEqual(doc.page_count, 8)
        page0 = doc[0]
        self.assertAlmostEqual(page0.rect.width, PAGE_W, delta=1)
        self.assertAlmostEqual(page0.rect.height, PAGE_H, delta=1)
        text = "\n".join(page.get_text("text") for page in doc)
        self.assertIn("All Users Are Created Equally By", text)
        self.assertIn("LIBERA OMNES UTENTES", text)
        self.assertIn("Holy Bible", text)
        self.assertIn("Genesis", text)
        self.assertIn("John", text)
        pix = page0.get_pixmap(matrix=pymupdf.Matrix(0.4, 0.4), alpha=False)
        avg = sum(pix.samples) / max(1, len(pix.samples))
        self.assertLess(avg, 80, "cover should be a dark page")
        names = doc.resolve_names() or {}
        self.assertIn("root-index", names)
        self.assertIn("b01c001", names)
        self.assertIn("b43c001", names)
        self.assertGreaterEqual(len(doc[0].get_links()), 3)
        chapter = next(page for page in doc if "Genesis - Chapter 1" in (page.get_text("text") or ""))
        self.assertGreaterEqual(len(chapter.get_links()), 4)




if __name__ == "__main__":
    unittest.main()
