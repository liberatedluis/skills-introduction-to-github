# Christ Supply Holy Bible — iPhone Matrix app

Native SwiftUI companion to the Christ Supply Holy Bible Matrix web reader. Same product, same indexes, same World English Bible text.

**Christ Supply Holy Bible** · **ChristSupply.Net**

Made by Liberated Luis With Cursor, Claude Opus, and MacBook

All Users Are Created Equally By God · LIBERA OMNES UTENTES | LIBERATE ALL USERS

## What it does

Launches on the **Root Index**. Tap a rainbow letter, theme, name, or library book, then tap a verse. The Matrix reader opens that World English Bible passage on the phone — no Safari chrome.

Navigation matches `assets/js/indexes.js`:

- Word of God → Genesis 1, John 1, Full Library
- Old / New Testament → book → chapter
- Rainbow (red, orange, gold, yellow, green, cyan, blue, purple, pink)
- Themes (THE LORD SAID, Do Not Be Afraid, mercy, believe, love, peace, sin, wrath)
- I AM, Arcs of God, Help Me Now God
- Women of God, Men of God
- Word Index, Word Roots

## Open on Liberateds-Mac-Studio

This folder is a complete Xcode iOS app. It was authored on Linux, so `xcodebuild` was not run here. Open it on the Mac that has Xcode.

1. Clone or pull this repo.
2. Double-click [`ChristSupplyMatrix.xcodeproj`](ChristSupplyMatrix.xcodeproj), or from Terminal:

   ```bash
   open ios/ChristSupplyMatrix.xcodeproj
   ```

3. In Xcode, set the run destination to an **iPhone** simulator (for example iPhone 16). This target is iPhone-first (`TARGETED_DEVICE_FAMILY = 1`), iOS 17+.
4. Signing & Capabilities → Team → choose your Apple ID / team on Liberateds-Mac-Studio. The bundle id is `net.christsupply.holybible`.
5. Product → Run (⌘R).

The home-screen name is **Christ Supply**. In-app chrome says **ChristSupply.Net** and **Christ Supply Holy Bible**.

## Bundled data

| File | Source | Role |
| --- | --- | --- |
| `../data/indexes.json` | Extracted from the constitutional dark offline WEB PDF | Clickable study indexes |
| `../data/books.json` | Protestant 66-book map | Book names and chapter counts |
| `ChristSupplyMatrix/Resources/web-chapters.json` | Public-domain World English Bible (`getbible` `web` / eBible `engwebp`) | Offline chapter text |

Tapping an index verse reads the bundled WEB chapter first. If a chapter is missing, the app fetches `https://api.getbible.net/v2/web/{book}/{chapter}.json` (same text the web reader uses for WEB) and caches it in memory.

Refresh the bundled WEB text:

```bash
python3 scripts/bundle_web_chapters.py
```

## Project layout

```
ios/
  ChristSupplyMatrix.xcodeproj/   Xcode project
  ChristSupplyMatrix/             SwiftUI sources + assets
  project.yml                     XcodeGen spec (optional regenerate)
  README.md
```

If you use [XcodeGen](https://github.com/yonaskolb/XcodeGen), `project.yml` can rebuild the `.xcodeproj`. The checked-in project is already openable without XcodeGen.

## Notes

- Default translation is the public-domain **World English Bible**.
- The existing web Matrix in `index.html` is unchanged.
- This Linux worker cannot compile for iOS. After you Run on the Mac, the first path to try is Root Index → Red Letter → a book → a verse.
