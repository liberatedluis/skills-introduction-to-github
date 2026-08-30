# Christ Supply Holy Bible

**1,300 translations.** Three ways to read. Every page is marked **ChristSupply.Net**.

Made by Liberated Luis With Cursor, Claude Opus, and MacBook · [ChristSupply.Net](https://christsupply.net)

## 1. Matrix scroll (HTML)

Open [`index.html`](index.html). Search a language or translation, then keep scrolling — the next chapter loads as you go.

Live: [liberatedluis.github.io/skills-introduction-to-github](https://liberatedluis.github.io/skills-introduction-to-github/)

```bash
python3 scripts/serve.py --port 8080
```

Then open `http://localhost:8080`.

## 2. Print HTML

Same reader, **Format → PDF**, then Print / Save PDF. Or browse all 1,300 translations as HTML cards: [`print.html`](print.html).

## 3. Print PDFs

6×9 inch Bibles in [`print-bibles/`](print-bibles/) (Git LFS). Example:

`print-bibles/E/English/Full Bible — World English Bible.pdf`

```bash
git lfs install
git lfs pull
python3 -m pip install -r requirements.txt
python3 scripts/make_holy_bible_pdfs.py --workers 4
```

## Credits

Scripture remains with its translators and publishers. This project prefers public-domain and redistributable editions.

Also: [Charter](charter/) — a civic reader of the Declaration, Constitution, and Bill of Rights.

Christ Supply Holy Bible · Made by Liberated Luis With Cursor, Claude Opus, and MacBook · ChristSupply.Net
