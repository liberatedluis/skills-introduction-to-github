# Charter

Three public-domain US founding texts:

1. The Declaration of Independence
2. The Constitution of the United States (preamble, articles, sections, clauses)
3. The Bill of Rights (Amendments I–X), then later amendments so the Constitution is whole

Web. Light and dark PDFs. iPhone app. Every surface has the same bites. Free. No ads, accounts, or tracking. Not a Bible app.

Created by Liberated Luis / Christ Supply.

## 1. Web reader

```bash
cd charter && python3 -m http.server 8765
```

http://localhost:8765

From the repo root: `python3 scripts/serve.py --port 8080` then `/charter/`.

One thought per screen. Hash URLs. Copy / Share. Contents. Parchment and dark mode. Offline after the first load.

Examples: `#/declaration/grievance-17` · `#/constitution/preamble` · `#/rights/1` · `#/later/11`

## 2. Light and dark PDFs

One thought per page, 6×9. Every book, both editions:

| Book | Light | Dark |
| --- | --- | --- |
| Charter (all three) | [charter-light.pdf](pdfs/charter-light.pdf) | [charter-dark.pdf](pdfs/charter-dark.pdf) |
| Declaration | [declaration-light.pdf](pdfs/declaration-light.pdf) | [declaration-dark.pdf](pdfs/declaration-dark.pdf) |
| Constitution | [constitution-light.pdf](pdfs/constitution-light.pdf) | [constitution-dark.pdf](pdfs/constitution-dark.pdf) |
| Bill of Rights and later amendments | [rights-light.pdf](pdfs/rights-light.pdf) | [rights-dark.pdf](pdfs/rights-dark.pdf) |

Print preview: [print.html](print.html) · [print.html?theme=dark](print.html?theme=dark)

```bash
node make_pdfs.mjs
```

## 3. iPhone app

Native SwiftUI in [`ios/`](ios/). Same texts, the whole PDF library, share (web URL + `charter://`), contents, dark/light, offline. iPhone and iPad.

```bash
open ios/Charter.xcodeproj
```

Set your signing team, run on an iPhone or iPad. iOS 17+. After text changes: `node ios/export_bundle.mjs`. See [ios/README.md](ios/README.md).

## Texts

National Archives transcriptions. Not paraphrased. Short labels never replace the original words.

- [Declaration](https://www.archives.gov/founding-docs/declaration-transcript)
- [Constitution](https://www.archives.gov/founding-docs/constitution-transcript)
- [Bill of Rights](https://www.archives.gov/founding-docs/bill-of-rights-transcript)
- [Amendments XI–XXVII](https://www.archives.gov/founding-docs/amendments-11-27)

No Federalist Papers.

```bash
node test_texts.mjs
```

## Footer

Created by Christ Supply, [Support Here](https://christ.supply/support-us).
