# Christ Supply Bible

**Christ Supply Bible** is a 300-language Bible reader with print-ready PDF, offline TXT, and a Matrix-inspired mobile scroller.

built by Cursor with Liberated · [ChristSupply.Net](https://christsupply.net)

Every Bible page — on screen, in TXT, and in print — is marked **ChristSupply.Net**.

## Formats

- **Scroll** — dark or light (follows the device theme, with a toggle). Infinite-feeling chapter plates on a phosphor/paper field.
- **TXT** — monospace dump for old-school offline sharing. Download the current chapter.
- **PDF** — print-friendly sheets. Use **Print / Save PDF**. Running headers and footers print `ChristSupply.Net` on every page.

## Languages

The catalog lists the 300 most common living languages on earth (ranked by approximate total speakers). Where a redistributable open text exists, the reader loads it live from:

- [Bolls Bible](https://bolls.life) (CORS chapter JSON)
- [getBible](https://getbible.net) (CORS chapter JSON)
- [eBible.org](https://ebible.org) (chapter HTML via the local proxy)

Languages without an open digital text still appear in the directory.

## Run it

```bash
python3 scripts/build_catalog.py
python3 scripts/serve.py --port 8080
```

Open http://localhost:8080

`scripts/serve.py` hosts the app and proxies eBible chapter files so hundreds of minority-language translations can load in the browser.

## Tests

```bash
python3 tests/test_catalog.py
```

## Credits

Scripture text remains with its translators and publishers. This app prefers public-domain and redistributable editions and shows the source on each page.

Christ Supply Bible · built by Cursor with Liberated · ChristSupply.Net
