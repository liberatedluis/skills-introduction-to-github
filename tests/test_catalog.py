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
        self.assertIn('id="glossary"', html)
        self.assertIn('id="glossaryBtn"', html)
        self.assertIn("Chapter glossary", html)
        self.assertIn("size: letter", css)
        self.assertIn("chapterHref", js)
        self.assertIn("renderGlossaryPanel", js)
        self.assertIn("glossarySheetHtml", js)

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
        from make_holy_bible_pdfs import build_catalog

        catalog = build_catalog()
        self.assertEqual(len(catalog), 1300)
        self.assertEqual(len({row["id"] for row in catalog}), 1300)
        self.assertTrue(any(row["id"] == "engwebp" for row in catalog))

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

    def test_chapter_glossary_structure(self):
        from make_holy_bible_pdfs import PAGE_SIZE, books_and_chapters, group_chapters

        self.assertEqual(PAGE_SIZE, "Letter")
        verses = [
            ("GEN", 1, 1, "In the beginning"),
            ("GEN", 1, 2, "And the earth"),
            ("GEN", 2, 1, "Thus the heavens"),
            ("EXO", 1, 1, "Now these are"),
            ("EXO", 1, 2, "Reuben"),
        ]
        grouped = group_chapters(verses)
        self.assertEqual([(book, ch, len(items)) for book, ch, items in grouped], [("GEN", 1, 2), ("GEN", 2, 1), ("EXO", 1, 2)])
        self.assertEqual(books_and_chapters(grouped), [("GEN", [1, 2]), ("EXO", [1])])

    def test_letter_pdf_has_glossary_links(self):
        import tempfile

        import pypdfium2 as pdfium

        from make_holy_bible_pdfs import write_pdf

        verses = []
        for chapter in range(1, 4):
            for verse in range(1, 6):
                verses.append(("GEN", chapter, verse, f"Verse {chapter}:{verse} of the test Bible."))
        for verse in range(1, 4):
            verses.append(("JHN", 3, verse, f"For God so loved the world {verse}."))
        meta = {
            "id": "test-letter",
            "title": "Test Letter Bible",
            "language": "English",
            "native": "English",
            "script": "Latin",
            "rtl": False,
            "copyright": "Public Domain",
            "coverage": "portions",
        }
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "test.pdf"
            write_pdf(meta, verses, dest)
            data = dest.read_bytes()
            doc = pdfium.PdfDocument(str(dest))
            try:
                pages = [page.get_textpage().get_text_bounded() for page in doc]
            finally:
                doc.close()
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertIn(b"/Annot", data)
        self.assertIn(b"/Outlines", data)
        self.assertIn(b"/MediaBox [0 0 612.00 792.00]", data)
        self.assertGreaterEqual(len(pages), 3)
        self.assertIn("US Letter", pages[0])
        self.assertIn("Chapter glossary", pages[0])
        self.assertNotIn("p.1", pages[0])
        self.assertIn("Chapter glossary", pages[1])
        self.assertIn("Genesis", pages[1])
        self.assertIn("John", pages[1])
        self.assertIn("Genesis 1", pages[2])
        self.assertIn("John 3", pages[2])

    def test_full_bible_glossary_fits_one_page(self):
        from make_holy_bible_pdfs import HolyBiblePDF, font_for, write_chapter_glossary

        books = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
        book_chapters = [(row["usfm"], list(range(1, row["chapters"] + 1))) for row in books]
        self.assertEqual(sum(len(chaps) for _, chaps in book_chapters), 1189)
        pdf = HolyBiblePDF("English", font_for("Latin"), False)
        pdf.show_marks = True
        pdf.add_page()
        write_chapter_glossary(pdf, book_chapters, lambda book, ch: pdf.get_named_destination(f"ch-{book}-{ch}"))
        self.assertEqual(pdf.page_no(), 1)

    def test_copy_force_overwrites(self):
        import tempfile

        from copy_holy_bibles_to_desktop import place

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.pdf"
            src2 = Path(tmp) / "src2.pdf"
            dest = Path(tmp) / "out" / "dest.pdf"
            src.write_bytes(b"%PDF-1.3 old")
            first = place(src, dest)
            self.assertIn(first, {"link", "copy"})
            self.assertEqual(place(src, dest), "exists")
            src2.write_bytes(b"%PDF-1.3 new-bytes")
            self.assertIn(place(src2, dest, force=True), {"link", "copy"})
            self.assertEqual(dest.read_bytes(), b"%PDF-1.3 new-bytes")







if __name__ == "__main__":
    unittest.main()
