# Christ Supply Holy Bible

**Christ Supply Holy Bible** is **1,300 scrollable Matrix translations** plus matching 6×9 print PDFs.

Made by Liberated Luis With Cursor, Claude Opus, and MacBook · [ChristSupply.Net](https://christsupply.net)

Every Bible page — on screen, in TXT, and in print — is marked **ChristSupply.Net**.

## Formats

- **Scroll** — Matrix rain, dark or light, with continuous chapter scrolling through all 1,300 open translations.
- **TXT** — monospace dump for old-school offline sharing.
- **PDF** — 6×9 print Bibles. Header and footer on every page: ChristSupply.Net, Christ Supply Holy Bible, and *Made by Liberated Luis With Cursor, Claude Opus, and MacBook*.

## 1,300 Matrix Holy Bibles

The 1,300 Matrix scrollables are in [`scroll-bibles/`](scroll-bibles/) — letter folders, then language, same layout as the print PDFs.

- GitHub: [`scroll-bibles/E/English`](scroll-bibles/E/English)
- GitHub Pages: https://liberatedluis.github.io/skills-introduction-to-github/scroll-bibles/ (turn on **Settings → Pages → GitHub Actions** once, then re-run **Publish GitHub Pages**)

```bash
python3 scripts/make_scroll_bibles.py
python3 scripts/serve.py --port 8080
```

Open `http://localhost:8080/scroll-bibles/` or a language folder such as `http://localhost:8080/scroll-bibles/E/English/`.

The live reader at `http://localhost:8080` also searches all 1,300. `print.html` is the searchable catalog.

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
