# Charter

A spreadable, mindfully edible civic reader of three public-domain US founding texts:

1. The Declaration of Independence
2. The Constitution of the United States (preamble, articles, sections, clauses)
3. The Bill of Rights (Amendments I–X), with a path into later amendments so the Constitution is whole

Created by Liberated Luis / Christ Supply. Free. No ads, accounts, or tracking. This is a civic reader, not a Bible app.

## Open it

From this folder:

```bash
python3 -m http.server 8765
```

Then open [http://localhost:8765](http://localhost:8765).

Or, from the repo root:

```bash
python3 scripts/serve.py --port 8080
```

Then open [http://localhost:8080/charter/](http://localhost:8080/charter/).

`index.html` is static HTML, CSS, and JS. After the first load on http(s), a service worker keeps the reader offline.

## How it reads

- Home is a table of the three documents.
- One bite per screen: a clause, a grievance, a self-evident truth, or one amendment.
- Next / Prev, swipe, or arrow keys. A contents rail (drawer on a phone) jumps to any bite.
- Every bite has a stable hash URL, for example `#/declaration/grievance-17` or `#/constitution/preamble`.
- **Copy** and **Share** use the Web Share API, with clipboard as fallback.
- Cream / parchment by default, with a dark mode. Progress shows where you are, without scores.

Deep links restore the exact bite after a reload.

## PDFs

One thought per page, in both parchment and dark editions:

- [pdfs/charter-light.pdf](pdfs/charter-light.pdf)
- [pdfs/charter-dark.pdf](pdfs/charter-dark.pdf)

Rebuild after text or layout changes:

```bash
node make_pdfs.mjs
```

Print preview (then browser Print / Save as PDF): [print.html](print.html) or `print.html?theme=dark`.

## Texts

Legal wording is the National Archives transcriptions. It is not paraphrased. Short labels (for example “Commerce”) sit above the original words and never replace them.

- [Declaration of Independence](https://www.archives.gov/founding-docs/declaration-transcript)
- [Constitution](https://www.archives.gov/founding-docs/constitution-transcript)
- [Bill of Rights](https://www.archives.gov/founding-docs/bill-of-rights-transcript)
- [Amendments XI–XXVII](https://www.archives.gov/founding-docs/amendments-11-27)

The Federalist Papers are not included.

```bash
node test_texts.mjs
```

## Footer

Created by Christ Supply, [Support Here](https://christ.supply/support-us).
