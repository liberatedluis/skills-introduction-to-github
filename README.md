# Christ Supply Holy Bible

**Christ Supply Holy Bible** is **1,300 scrollable Matrix translations** plus matching 6×9 print PDFs.

Made by Liberated Luis With Cursor, Claude Opus, and MacBook · [ChristSupply.Net](https://christsupply.net)

Every Bible page — on screen, in TXT, and in print — is marked **ChristSupply.Net**.

## Formats

- **Scroll** — Matrix rain, dark or light, with continuous chapter scrolling through all 1,300 open translations.
- **Index** — clickable Root Index from the English WEB offline packet: rainbow letters, I AM THE LORD, Arcs of God, Word Index, and people indexes. Tap a verse to open it in the Matrix scroller.
- **TXT** — monospace dump for old-school offline sharing.
- **PDF** — 6×9 print Bibles. Header and footer on every page: ChristSupply.Net, Christ Supply Holy Bible, and *Made by Liberated Luis With Cursor, Claude Opus, and MacBook*.
- **Offline app** — phone-sized dark WEB packet with clickable pages: [offline-app.html](offline-app.html). Constitutional header: *All Users Are Created Equally By God*. Build the matching PDF with `python3 scripts/make_constitutional_pdf.py`.

## 1,300 Matrix Holy Bibles

The reader searches the same 1,300 redistributable editions used for print: [eBible.org](https://ebible.org) texts plus public-domain getBible extras. Type a language, ISO code, or translation name, then keep scrolling — the next chapter loads as you go.

```bash
python3 scripts/build_catalog.py
python3 scripts/serve.py --port 8080
```

Open `http://localhost:8080` for the scroller (Format → Index for the clickable WEB indexes), `offline-app.html` for the constitutional dark clickable WEB reader, and `print.html` for the 1,300-translation catalog.

## Constitutional dark offline app (English WEB)

Phone-sized pages, tap targets for every book and chapter, and highlighted names of God. The PDF is the offline reading packet:

```bash
python3 scripts/make_constitutional_pdf.py --sample
python3 scripts/make_constitutional_pdf.py
```

That writes `pdfs/christ-supply-english-bible-constitutional-dark-offline-app-clickable-pages.pdf`. Every page keeps the constitutional mark and footer links for Source, Contents, and Share.


## 1,300 translation PDFs

Open, redistributable texts written as print PDFs in `pdfs/holy-bibles/`.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/make_holy_bible_pdfs.py --workers 4
python3 scripts/make_holy_bible_pdfs.py --only engwebp
```

Each file is named `ChristSupplyHolyBible-{translationId}.pdf`.

On GitHub they live under [`print-bibles/`](print-bibles/) as language folders (Git LFS):

`print-bibles/E/English/Full Bible — World English Bible.pdf`

Clone with Git LFS, then the PDFs come down with the repo:

```bash
git lfs install
git clone https://github.com/liberatedluis/skills-introduction-to-github.git
cd skills-introduction-to-github
git lfs pull
```

## Folders on your Desktop

After the PDFs exist, put them in language folders on your Mac Desktop:

```bash
python3 scripts/copy_holy_bibles_to_desktop.py
```

Or double-click `scripts/copy-to-desktop.command`. That creates:

`Desktop/Christ Supply Holy Bible/E/English/Full Bible — World English Bible.pdf`

Letter folders A–Z, then one folder per language. English, Spanish, Hebrew, and other languages with several editions share a folder.

## Tests

```bash
python3 tests/test_catalog.py
```

## Credits

Scripture remains with its translators and publishers. This project prefers public-domain and redistributable editions and prints the source copyright on each cover.

Live reader: [liberatedluis.github.io/skills-introduction-to-github](https://liberatedluis.github.io/skills-introduction-to-github/)

Christ Supply Holy Bible · Made by Liberated Luis With Cursor, Claude Opus, and MacBook · ChristSupply.Net
