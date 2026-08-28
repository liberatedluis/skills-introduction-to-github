# Christ Supply Holy Bible — 1,300 print PDFs

Made by Liberated Luis With Cursor, Claude Opus, and MacBook · ChristSupply.Net

```bash
python3 -m pip install -r requirements.txt
python3 scripts/make_holy_bible_pdfs.py --workers 4
python3 scripts/make_holy_bible_pdfs.py --only heb --force
python3 scripts/copy_holy_bibles_to_desktop.py
```

That last command puts the 1,300 PDFs in language folders on your Desktop:

`Desktop/Christ Supply Holy Bible/E/English/`


Every page header/footer carries **ChristSupply.Net**, **Christ Supply Holy Bible**, and the maker line. Files are US Letter. Page 2 is a clickable chapter glossary.
