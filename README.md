# Christ Supply Holy Bible

**Christ Supply Holy Bible** is a 300-language reader plus **1,300 print-ready translation PDFs**.

Made by Liberated Luis With Cursor, Claude Opus, and MacBook · [ChristSupply.Net](https://christsupply.net)

Every Bible page — on screen, in TXT, and in print — is marked **ChristSupply.Net**.

## Formats

- **Scroll** — dark or light (follows the device theme, with a toggle).
- **TXT** — monospace dump for old-school offline sharing.
- **PDF** — US Letter print Bibles with a clickable chapter glossary. Header and footer on every page: ChristSupply.Net, Christ Supply Holy Bible, and *Made by Liberated Luis With Cursor, Claude Opus, and MacBook*. Print at 100% / Actual size.

## 1,300 translation PDFs

Open, redistributable texts from [eBible.org](https://ebible.org) (1,291) plus 9 public-domain editions from getBible, written as print PDFs in `pdfs/holy-bibles/`.

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
git checkout cursor/holy-bible-1300-print-pdfs-9e43
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


## Languages

The web catalog lists the 300 most common living languages. Live text loads from Bolls, getBible, and eBible where an open edition exists.

## Run the reader

```bash
python3 scripts/build_catalog.py
python3 scripts/serve.py --port 8080
```

## Tests

```bash
python3 tests/test_catalog.py
```

## Credits

Scripture remains with its translators and publishers. This project prefers public-domain and redistributable editions and prints the source copyright on each cover.

Live reader: [liberatedluis.github.io/skills-introduction-to-github](https://liberatedluis.github.io/skills-introduction-to-github/)

Christ Supply Holy Bible · Made by Liberated Luis With Cursor, Claude Opus, and MacBook · ChristSupply.Net
