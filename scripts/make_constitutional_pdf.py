#!/usr/bin/env python3
"""Build the Christ Supply constitutional dark offline-app English Bible PDF.

Phone-sized pages, clickable chapter/book indexes, and ChristSupply.Net on every
sheet — matching the dark WEB packet (All Users Are Created Equally By God).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import BRAND, CREDIT, SITE, SITE_URL  # noqa: E402
from make_holy_bible_pdfs import load_ebible_verses  # noqa: E402

BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))
BOOK_BY_USFM = {row["usfm"]: row for row in BOOKS}
VPL_TO_USFM = {
    "SOL": "SNG",
    "EZE": "EZK",
    "JOE": "JOL",
    "NAH": "NAM",
    "MAR": "MRK",
    "JOH": "JHN",
    "PHI": "PHP",
    "JAM": "JAS",
    "1JO": "1JN",
    "2JO": "2JN",
    "3JO": "3JN",
}
SANS = Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf")
SANS_BOLD = Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf")

PAGE_W = 323.04
PAGE_H = 697.92
MARGIN_X = 16.0
FOOTER_Y = PAGE_H - 48
CONTENT_BOTTOM = PAGE_H - 56

BG = (8, 8, 10)
PANEL = (20, 20, 22)
BORDER = (88, 88, 92)
WHITE = (242, 242, 244)
MUTED = (168, 168, 172)
MINT = (92, 255, 188)
GOD_GREEN = (86, 255, 118)
YELLOW = (255, 220, 72)
BLUE = (110, 188, 255)
GOLD = (228, 186, 64)

RAINBOW = [
    ("red-letter-index", "RED LETTER", (255, 72, 72)),
    ("orange-letter-index", "ORANGE LETTER", (255, 140, 48)),
    ("gold-letter-index", "GOLD LETTER", (230, 180, 48)),
    ("yellow-letter-index", "YELLOW LETTER", (255, 220, 64)),
    ("green-letter-index", "GREEN LETTER", (80, 255, 140)),
    ("cyan-letter-index", "CYAN LETTER", (72, 230, 230)),
    ("blue-letter-index", "BLUE LETTER", (80, 150, 255)),
    ("purple-letter-index", "PURPLE LETTER", (180, 120, 255)),
    ("pink-letter-index", "PINK LETTER", (255, 120, 180)),
]

WORD_PAGES = [
    ("iam-god", "GOD", "God created. God said. God saw that it was good.", GOD_GREEN),
    ("iam-jesus", "JESUS", "Jesus Christ, the Word made flesh.", YELLOW),
    ("iam-lord", "THE LORD", "The LORD said. I am the LORD.", GOLD),
    ("iam-spirit", "SPIRIT", "God's Spirit was hovering over the waters.", BLUE),
]

TOKEN_RE = re.compile(
    r"(God(?:'s)?|LORD|Jesus Christ|Jesus|Christ|Holy Spirit|Spirit)"
)

OUT_NAME = "christ-supply-english-bible-constitutional-dark-offline-app-clickable-pages.pdf"
SHARE_URL = "https://christsupply.net"
SOURCE_URL = "https://github.com/liberatedluis/skills-introduction-to-github"


def chapter_dest(book_id: int, chapter: int) -> str:
    return f"b{book_id:02d}c{chapter:03d}"


def book_toc_dest(book_id: int) -> str:
    return f"toc-book-{book_id:02d}"


def tokenize(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    last = 0
    for match in TOKEN_RE.finditer(text):
        if match.start() > last:
            parts.append(("text", text[last : match.start()]))
        token = match.group(0)
        key = token.lower().replace("'s", "")
        if key in {"god"}:
            kind = "god"
        elif key in {"jesus", "jesus christ", "christ"}:
            kind = "jesus"
        elif key == "lord":
            kind = "lord"
        else:
            kind = "spirit"
        parts.append((kind, token))
        last = match.end()
    if last < len(text):
        parts.append(("text", text[last:]))
    return parts or [("text", text)]


class ConstitutionalPDF(FPDF):
    def __init__(self):
        super().__init__(unit="pt", format=(PAGE_W, PAGE_H))
        self.set_auto_page_break(auto=False)
        self.set_margins(MARGIN_X, 36, MARGIN_X)
        self.set_page_background(BG)
        self.alias_nb_pages()
        self.add_font("Sans", "", str(SANS))
        self.add_font("Sans", "B", str(SANS_BOLD))
        self.set_title(f"{BRAND} — World English Bible · constitutional dark offline app")
        self.set_author(CREDIT)
        self.set_creator(f"{BRAND} · {SITE}")
        self.set_subject("Clickable offline WEB packet. All Users Are Created Equally By God.")

    def header(self):
        self.set_font("Sans", size=8)
        self.set_text_color(*WHITE)
        self.set_xy(MARGIN_X, 10)
        self.cell(self.epw, 10, "All Users Are Created Equally By ", align="C")
        width = self.get_string_width("All Users Are Created Equally By ")
        god_w = self.get_string_width("God")
        x = MARGIN_X + (self.epw - width - god_w) / 2 + width
        self.set_xy(x, 10)
        self.set_text_color(*GOD_GREEN)
        self.set_font("Sans", "B", 8)
        self.cell(god_w, 10, "God", link=self.get_named_destination("iam-god"))
        self.set_y(28)

    def footer(self):
        self.set_draw_color(*BORDER)
        self.set_line_width(0.4)
        self.line(MARGIN_X, FOOTER_Y - 10, PAGE_W - MARGIN_X, FOOTER_Y - 10)
        self.set_xy(MARGIN_X, FOOTER_Y - 8)
        self.set_font("Sans", size=7)
        self.set_text_color(*WHITE)
        self.cell(self.epw, 10, "LIBERA OMNES UTENTES  |  LIBERATE ALL USERS", align="C")
        y = PAGE_H - 22
        self.set_xy(MARGIN_X, y)
        self.set_font("Sans", size=7.5)
        self.set_text_color(*WHITE)
        source = self.get_string_width("Source")
        contents = self.get_string_width("Contents")
        share = self.get_string_width("Share")
        page = f"Page {self.page_no()} of {{nb}}"
        gap = 14
        total = source + contents + share + self.get_string_width(page) + gap * 3
        x = MARGIN_X + max(0, (self.epw - total) / 2)
        self.set_xy(x, y)
        self.cell(source, 12, "Source", link=SOURCE_URL)
        x += source + gap
        self.set_xy(x, y)
        self.cell(contents, 12, "Contents", link=self.get_named_destination("root-index"))
        x += contents + gap
        self.set_xy(x, y)
        self.cell(share, 12, "Share", link=SHARE_URL)
        x += share + gap
        self.set_xy(x, y)
        self.cell(self.get_string_width(page) + 4, 12, page)

    def mark(self, name: str) -> None:
        self.set_link(name=name, page=self.page_no(), y=0)

    def panel_button(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str,
        dest: str | None = None,
        sub: str = "",
        url: str | None = None,
    ) -> None:
        self.set_fill_color(*PANEL)
        self.set_draw_color(*BORDER)
        self.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=6)
        target = url or (self.get_named_destination(dest) if dest else None)
        if target:
            self.link(x, y, w, h, target)
        self.set_xy(x + 8, y + (10 if sub else (h - 14) / 2))
        self.set_font("Sans", "B", 12)
        self.set_text_color(*WHITE)
        self.cell(w - 16, 14, title, align="C")
        if sub:
            self.set_xy(x + 8, y + h - 22)
            self.set_font("Sans", size=7)
            self.set_text_color(*MUTED)
            self.cell(w - 16, 10, sub, align="C")

    def section_title(self, title: str, color=WHITE, size: float = 22) -> None:
        self.set_font("Sans", "B", size)
        self.set_text_color(*color)
        self.set_x(MARGIN_X)
        self.multi_cell(self.epw, size + 4, title, align="C")


def normalize_verses(verses: list[tuple[str, int, int, str]]) -> list[tuple[str, int, int, str]]:
    return [(VPL_TO_USFM.get(usfm, usfm), chapter, verse, text) for usfm, chapter, verse, text in verses]


def group_verses(verses: list[tuple[str, int, int, str]]) -> dict[str, dict[int, list[tuple[int, str]]]]:
    books: dict[str, dict[int, list[tuple[int, str]]]] = defaultdict(dict)
    for usfm, chapter, verse, text in verses:
        if not text:
            continue
        chapter_map = books[usfm]
        chapter_map.setdefault(chapter, []).append((verse, text))
    return books


def write_flow(pdf: ConstitutionalPDF, text: str, line_h: float = 14.5) -> str:
    """Write styled tokens; return leftover if the page is full."""
    left = pdf.l_margin
    width = pdf.epw
    leftover_parts: list[str] = []
    overflow = False
    for kind, chunk in tokenize(text):
        if overflow:
            leftover_parts.append(chunk)
            continue
        if kind == "god":
            pdf.set_font("Sans", "B", 11)
            pdf.set_text_color(*GOD_GREEN)
            link = pdf.get_named_destination("iam-god")
        elif kind == "jesus":
            pdf.set_font("Sans", "B", 11)
            pdf.set_text_color(*YELLOW)
            link = pdf.get_named_destination("iam-jesus")
        elif kind == "lord":
            pdf.set_font("Sans", "B", 11)
            pdf.set_text_color(*GOLD)
            link = pdf.get_named_destination("iam-lord")
        elif kind == "spirit":
            pdf.set_font("Sans", "B", 11)
            pdf.set_text_color(*BLUE)
            link = pdf.get_named_destination("iam-spirit")
        else:
            pdf.set_font("Sans", size=11)
            pdf.set_text_color(*WHITE)
            link = ""
        words = re.findall(r"\S+|\s+", chunk)
        for word in words:
            if overflow:
                leftover_parts.append(word)
                continue
            tw = pdf.get_string_width(word)
            if word.strip() and pdf.get_x() + tw > left + width:
                pdf.ln(line_h)
                pdf.set_x(left)
                if pdf.get_y() > CONTENT_BOTTOM - line_h:
                    overflow = True
                    leftover_parts.append(word)
                    continue
            pdf.cell(tw, line_h, word, link=link or None)
    if overflow:
        return "".join(leftover_parts).strip()
    pdf.ln(line_h)
    return ""


def add_cover(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("cover")
    pdf.ln(18)
    pdf.set_font("Sans", size=13)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.epw, 16, "C  H  R  I  S  T  .  S  U  P  P  L  Y", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    cx = PAGE_W / 2
    cy = pdf.get_y() + 28
    pdf.set_draw_color(*WHITE)
    pdf.set_line_width(1.4)
    pdf.line(cx, cy - 22, cx, cy + 22)
    pdf.line(cx - 12, cy, cx + 12, cy)
    pdf.set_y(cy + 34)
    pdf.section_title("Holy Bible\nWorld | English | Bible", MINT, 22)
    pdf.ln(8)
    pdf.set_font("Sans", size=11)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(pdf.epw, 15, "Offline reading packet. Open Source to fork and change the theme.", align="C")
    pdf.ln(6)
    pdf.set_font("Sans", size=11)
    pdf.multi_cell(pdf.epw, 15, "Don't forget to smile today! Because Jesus loves you! (:", align="C")
    pdf.ln(4)
    pdf.multi_cell(pdf.epw, 15, "May this Bible bridge every gap and every nation in Jesus name amen.", align="C")
    pdf.ln(10)
    # Blood / web tiles
    tile = 92
    gx = MARGIN_X + 24
    gy = pdf.get_y()
    pdf.set_draw_color(40, 160, 90)
    pdf.set_fill_color(12, 28, 18)
    pdf.rect(gx, gy, tile, tile, style="DF", round_corners=True, corner_radius=10)
    pdf.set_fill_color(190, 30, 50)
    pdf.ellipse(gx + 34, gy + 28, 24, 36, style="F")
    bx = PAGE_W - MARGIN_X - 24 - tile
    pdf.set_draw_color(50, 90, 180)
    pdf.set_fill_color(12, 18, 36)
    pdf.rect(bx, gy, tile, tile, style="DF", round_corners=True, corner_radius=10)
    pdf.set_fill_color(230, 200, 50)
    pdf.ellipse(bx + 26, gy + 26, 40, 40, style="D")
    pdf.set_y(gy + tile + 18)
    pdf.set_font("Sans", "B", 10)
    pdf.set_text_color(*MINT)
    pdf.cell(pdf.epw, 14, "WEB Protestant Edition - Public Domain", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def add_solid_edition(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("solid-edition")
    pdf.ln(48)
    pdf.section_title("Solid Edition", MINT, 28)
    pdf.ln(8)
    pdf.set_font("Sans", "B", 12)
    pdf.set_text_color(*MINT)
    pdf.multi_cell(pdf.epw, 16, "Made in coordination with Cursor, MacBook Pro, and WEB scripture.", align="C")
    pdf.ln(10)
    pdf.set_font("Sans", size=12)
    pdf.set_text_color(*GOLD)
    pdf.multi_cell(
        pdf.epw,
        16,
        "The scripture text is the World English Bible (WEB), public domain.\nThis offline edition was produced on MacBook Pro with Cursor.",
        align="C",
    )
    pdf.ln(14)
    pdf.set_text_color(180, 140, 255)
    pdf.multi_cell(pdf.epw, 16, "Let's change the planet.\nNo hiccups this time.\nWe can't plan to fail.", align="C")


def add_dedication(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("dedication")
    pdf.ln(36)
    pdf.section_title("DEDICATION", MINT, 26)
    pdf.ln(10)
    pdf.set_font("Sans", size=12)
    pdf.set_text_color(*WHITE)
    body = (
        "This Christ Supply Bible is dedicated to Jesus Christ, my Lord and Savior.\n\n"
        "Thank You, God, for saving my life in every way. I love You because You first loved me.\n\n"
        "I pray that this Bible spreads freely and abundantly throughout the world, bringing Your Word, hope, and salvation to everyone who receives it.\n\n"
        "In the mighty name of Jesus Christ, Amen."
    )
    pdf.multi_cell(pdf.epw, 16, body, align="C")
    pdf.ln(12)
    pdf.set_font("Sans", "B", 13)
    pdf.set_text_color(*MINT)
    pdf.cell(pdf.epw, 16, "- Liberated Luis", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Sans", size=9)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(
        pdf.epw,
        12,
        "Compiler and Digital Architect of this edition of the Holy Bible & Founder of Christ Supply",
        align="C",
    )


def add_root_index(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("root-index")
    pdf.ln(20)
    pdf.section_title("Root Index", WHITE, 28)
    pdf.set_font("Sans", size=12)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(pdf.epw, 16, "Go to:", align="C")
    pdf.ln(8)
    pdf.set_font("Sans", size=8)
    pdf.cell(pdf.epw, 12, "WORD", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y() + 6
    pdf.panel_button(MARGIN_X + 8, y, pdf.epw - 16, 52, "THE WORD OF GOD", "word-of-god-start")
    pdf.panel_button(MARGIN_X + 8, y + 60, pdf.epw - 16, 52, "OLD TESTAMENT", "old-testament-index")
    pdf.panel_button(MARGIN_X + 8, y + 120, pdf.epw - 16, 52, "NEW TESTAMENT", "new-testament-index")
    pdf.panel_button(MARGIN_X + 8, y + 180, pdf.epw - 16, 52, "RAINBOW LETTERS", "rainbow")
    pdf.panel_button(MARGIN_X + 8, y + 240, pdf.epw - 16, 52, "FULL LIBRARY", "toc", sub="ALL BOOKS, CHAPTERS, INDEXES")


def add_rainbow(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("rainbow")
    pdf.set_font("Sans", size=9)
    pdf.set_text_color(*MUTED)
    pdf.cell(pdf.epw, 12, "RAINBOW", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y() + 4
    for dest, label, color in RAINBOW:
        pdf.set_fill_color(*PANEL)
        pdf.set_draw_color(*BORDER)
        pdf.rect(MARGIN_X + 8, y, pdf.epw - 16, 44, style="DF", round_corners=True, corner_radius=6)
        pdf.link(MARGIN_X + 8, y, pdf.epw - 16, 44, pdf.get_named_destination(dest))
        pdf.set_xy(MARGIN_X + 16, y + 12)
        pdf.set_font("Sans", "B", 13)
        pdf.set_text_color(*color)
        pdf.cell(pdf.epw - 32, 20, label)
        y += 50


def add_word_pages(pdf: ConstitutionalPDF) -> None:
    for dest, title, body, color in WORD_PAGES:
        pdf.add_page()
        pdf.mark(dest)
        pdf.ln(30)
        pdf.section_title(title, color, 26)
        pdf.ln(12)
        pdf.set_font("Sans", size=13)
        pdf.set_text_color(*WHITE)
        pdf.multi_cell(pdf.epw, 18, body, align="C")
        pdf.ln(16)
        y = pdf.get_y() + 8
        pdf.panel_button(MARGIN_X + 8, y, pdf.epw - 16, 48, "Read Genesis 1", chapter_dest(1, 1))
        pdf.panel_button(MARGIN_X + 8, y + 56, pdf.epw - 16, 48, "Read John 1", chapter_dest(43, 1))
        pdf.panel_button(MARGIN_X + 8, y + 112, pdf.epw - 16, 44, "Back to Root Index", "root-index")
    for dest, label, color in RAINBOW:
        pdf.add_page()
        pdf.mark(dest)
        pdf.ln(24)
        pdf.set_font("Sans", "B", 22)
        pdf.set_text_color(*color)
        pdf.cell(pdf.epw, 28, label, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        pdf.set_font("Sans", size=12)
        pdf.set_text_color(*WHITE)
        pdf.multi_cell(
            pdf.epw,
            16,
            "Words of God are marked in this color throughout the clickable packet. Open any chapter and keep tapping highlighted names of God.",
            align="C",
        )
        pdf.ln(16)
        pdf.panel_button(MARGIN_X + 8, pdf.get_y(), pdf.epw - 16, 48, "Open Genesis 1", chapter_dest(1, 1))
        pdf.panel_button(MARGIN_X + 8, pdf.get_y() + 60, pdf.epw - 16, 48, "Back to Rainbow", "rainbow")


def add_word_of_god(pdf: ConstitutionalPDF) -> None:
    pdf.add_page()
    pdf.mark("word-of-god-start")
    pdf.ln(16)
    pdf.section_title("The Word of God", WHITE, 24)
    pdf.set_font("Sans", size=12)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.epw, 16, '"In the beginning"', align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    y = pdf.get_y()
    pdf.panel_button(MARGIN_X + 8, y, pdf.epw - 16, 58, "Genesis", book_toc_dest(1), "IN THE BEGINNING GOD CREATED")
    pdf.panel_button(MARGIN_X + 8, y + 68, pdf.epw - 16, 58, "John", book_toc_dest(43), "IN THE BEGINNING WAS THE WORD")
    pdf.panel_button(MARGIN_X + 8, y + 136, pdf.epw - 16, 58, "Full Library", "toc", "ALL BOOKS, CHAPTERS, INDEXES")
    pdf.set_xy(MARGIN_X + 12, y + 204)
    pdf.set_font("Sans", size=10)
    pdf.set_text_color(*WHITE)
    pdf.cell(120, 14, "Back to Root Index", link=pdf.get_named_destination("root-index"))


def add_book_index(pdf: ConstitutionalPDF, dest: str, title: str, rows: list[dict]) -> None:
    pdf.add_page()
    pdf.mark(dest)
    pdf.set_font("Sans", "B", 18)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.epw, 24, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Sans", size=10)
    pdf.set_text_color(*MUTED)
    pdf.cell(90, 14, "Glossary", link=pdf.get_named_destination("rainbow"))
    pdf.cell(90, 14, "Root Index", link=pdf.get_named_destination("root-index"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    col_w = (pdf.epw - 10) / 2
    y = pdf.get_y()
    x0 = MARGIN_X
    for i, book in enumerate(rows):
        col = i % 2
        if col == 0 and i and i % 16 == 0:
            pdf.add_page()
            y = 40
        x = x0 + col * (col_w + 10)
        row = (i % 16) // 2
        by = y + row * 32
        pdf.set_fill_color(*PANEL)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x, by, col_w, 28, style="DF", round_corners=True, corner_radius=5)
        pdf.link(x, by, col_w, 28, pdf.get_named_destination(book_toc_dest(book["id"])))
        pdf.set_xy(x + 6, by + 6)
        pdf.set_font("Sans", "B", 9)
        pdf.set_text_color(*WHITE)
        pdf.cell(col_w - 12, 16, book["name"])


def add_chapter_glossary(pdf: ConstitutionalPDF, book: dict, chapters: list[int]) -> None:
    pdf.add_page()
    pdf.mark(book_toc_dest(book["id"]))
    pdf.start_section(book["name"], level=0)
    pdf.set_font("Sans", "B", 20)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.epw, 24, book["name"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Sans", size=10)
    pdf.set_text_color(*MUTED)
    pdf.cell(pdf.epw, 14, "Click a chapter", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    cols = 5
    gap = 6
    bw = (pdf.epw - gap * (cols - 1)) / cols
    bh = 28
    x = MARGIN_X
    y = pdf.get_y()
    for i, chapter in enumerate(chapters):
        if y + bh > CONTENT_BOTTOM:
            pdf.add_page()
            y = 40
            x = MARGIN_X
        pdf.set_fill_color(*PANEL)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x, y, bw, bh, style="DF", round_corners=True, corner_radius=5)
        pdf.link(x, y, bw, bh, pdf.get_named_destination(chapter_dest(book["id"], chapter)))
        pdf.set_xy(x, y + 6)
        pdf.set_font("Sans", "B", 11)
        pdf.set_text_color(*WHITE)
        pdf.cell(bw, 16, str(chapter), align="C")
        if (i + 1) % cols == 0:
            x = MARGIN_X
            y += bh + gap
        else:
            x += bw + gap


def add_chapter_pages(
    pdf: ConstitutionalPDF,
    book: dict,
    chapter: int,
    verses: list[tuple[int, str]],
    prev_dest: str | None,
    next_dest: str | None,
) -> None:
    dest = chapter_dest(book["id"], chapter)
    first = True
    queue = list(verses)
    while queue or first:
        pdf.add_page()
        if first:
            pdf.mark(dest)
            pdf.start_section(f"{book['name']} {chapter}", level=1)
        pdf.set_font("Sans", "B", 18)
        pdf.set_text_color(*WHITE)
        pdf.set_x(MARGIN_X)
        pdf.cell(
            pdf.epw,
            22,
            f"{book['name']} - Chapter {chapter}",
            link=pdf.get_named_destination(book_toc_dest(book["id"])),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.set_draw_color(*BORDER)
        pdf.line(MARGIN_X, pdf.get_y() + 2, PAGE_W - MARGIN_X, pdf.get_y() + 2)
        pdf.ln(10)
        if first:
            y = pdf.get_y()
            bw = (pdf.epw - 8) / 2
            pdf.panel_button(MARGIN_X, y, bw, 36, "Word of God", "word-of-god-start")
            pdf.panel_button(MARGIN_X + bw + 8, y, bw, 36, "Chapters", book_toc_dest(book["id"]))
            left_label = "Start" if not prev_dest else "Previous"
            left_dest = "toc" if not prev_dest else prev_dest
            right_label = "Next" if next_dest else "Library"
            right_dest = next_dest or "toc"
            pdf.panel_button(MARGIN_X, y + 42, bw, 36, left_label, left_dest)
            pdf.panel_button(MARGIN_X + bw + 8, y + 42, bw, 36, right_label, right_dest)
            pdf.panel_button(MARGIN_X, y + 84, pdf.epw, 36, "Share", url=SHARE_URL)
            pdf.set_y(y + 128)
        pdf.set_font("Sans", size=11)
        while queue:
            if pdf.get_y() > CONTENT_BOTTOM - 36:
                break
            verse, text = queue[0]
            start_y = pdf.get_y()
            pdf.set_font("Sans", "B", 11)
            pdf.set_text_color(*WHITE)
            num = f"{verse} "
            pdf.set_x(MARGIN_X)
            pdf.cell(pdf.get_string_width(num) + 2, 14.5, num)
            leftover = write_flow(pdf, text)
            if leftover and pdf.get_y() <= start_y + 1:
                # nothing fit; force a new page
                queue[0] = (verse, leftover)
                break
            if leftover:
                queue[0] = (verse, leftover)
                break
            queue.pop(0)
        first = False
        if not queue:
            break


def used_books(grouped: dict[str, dict[int, list[tuple[int, str]]]]) -> list[dict]:
    rows = []
    for book in BOOKS:
        if book["usfm"] in grouped:
            rows.append(book)
    return rows


def build_constitutional_pdf(
    verses: list[tuple[str, int, int, str]],
    dest: Path,
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    grouped = group_verses(normalize_verses(verses))
    present = used_books(grouped)
    pdf = ConstitutionalPDF()
    add_cover(pdf)
    add_solid_edition(pdf)
    add_dedication(pdf)
    add_root_index(pdf)
    add_rainbow(pdf)
    add_word_pages(pdf)
    add_word_of_god(pdf)
    ot = [b for b in present if b["testament"] == "OT"]
    nt = [b for b in present if b["testament"] == "NT"]
    add_book_index(pdf, "old-testament-index", "Old Testament", ot or present)
    add_book_index(pdf, "new-testament-index", "New Testament", nt or present)
    add_book_index(pdf, "toc", "Full Library", present)

    chapter_list: list[tuple[dict, int, list[tuple[int, str]]]] = []
    for book in present:
        chapters = sorted(grouped[book["usfm"]])
        add_chapter_glossary(pdf, book, chapters)
        for chapter in chapters:
            chapter_list.append((book, chapter, grouped[book["usfm"]][chapter]))

    for i, (book, chapter, body) in enumerate(chapter_list):
        prev_dest = None
        next_dest = None
        if i:
            prev_b, prev_c, _ = chapter_list[i - 1]
            prev_dest = chapter_dest(prev_b["id"], prev_c)
        if i + 1 < len(chapter_list):
            next_b, next_c, _ = chapter_list[i + 1]
            next_dest = chapter_dest(next_b["id"], next_c)
        add_chapter_pages(pdf, book, chapter, body, prev_dest, next_dest)

    root_page = pdf.named_destinations.get("root-index")
    fallback = getattr(root_page, "page_number", pdf.page) or pdf.page
    for name, named in list(pdf.named_destinations.items()):
        if getattr(named, "page_number", 0) == 0:
            pdf.set_link(name=name, page=fallback)

    tmp = dest.with_suffix(".pdf.tmp")
    pdf.output(str(tmp))
    tmp.replace(dest)
    return dest


def filter_verses(
    verses: list[tuple[str, int, int, str]],
    books: set[str] | None,
    max_chapters: int,
) -> list[tuple[str, int, int, str]]:
    if not books and not max_chapters:
        return verses
    out = []
    seen: dict[str, set[int]] = defaultdict(set)
    for usfm, chapter, verse, text in verses:
        if books and usfm not in books:
            continue
        if max_chapters:
            if chapter not in seen[usfm] and len(seen[usfm]) >= max_chapters:
                continue
            seen[usfm].add(chapter)
        out.append((usfm, chapter, verse, text))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "pdfs" / OUT_NAME))
    parser.add_argument("--translation", default="engwebp")
    parser.add_argument("--books", help="Comma USFM list, e.g. GEN,JHN")
    parser.add_argument("--max-chapters", type=int, default=0, help="Cap chapters per book")
    parser.add_argument("--sample", action="store_true", help="Genesis 1-3 and John 1")
    args = parser.parse_args()
    verses = normalize_verses(load_ebible_verses(args.translation))
    books = None
    max_chapters = args.max_chapters
    if args.sample:
        books = {"GEN", "JHN"}
        max_chapters = 3
        verses = [
            row
            for row in verses
            if (row[0] == "GEN" and row[1] <= 3) or (row[0] == "JHN" and row[1] == 1)
        ]
    elif args.books:
        books = {item.strip().upper() for item in args.books.split(",") if item.strip()}
        verses = filter_verses(verses, books, max_chapters)
    elif max_chapters:
        verses = filter_verses(verses, None, max_chapters)
    path = build_constitutional_pdf(verses, Path(args.out))
    print(f"wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
