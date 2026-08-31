# Charter for iPhone

A native SwiftUI civic reader. Same three founding texts as the web app, plus both PDFs, offline, share, and dark/light. Not a Bible app.

## Open in Xcode

On a Mac:

```bash
cd charter/ios
open Charter.xcodeproj
```

1. Select the **Charter** target.
2. Set your **Team** under Signing & Capabilities (bundle id `supply.christ.Charter`).
3. Choose an iPhone simulator or your device.
4. Run.

Requires Xcode 15+ and iOS 17.

## What it includes

- Home table of the Declaration, Constitution, and Bill of Rights
- One bite per screen, swipe or Next / Prev
- Contents sheet
- Copy and the system share sheet (`charter://declaration/grievance-17`)
- Later amendments XI–XXVII
- Light and dark PDFs in-app (PDFKit)
- Theme: System / Light / Dark
- Continue where you left off
- Footer: Created by Christ Supply, [Support Here](https://christ.supply/support-us)

Texts are the National Archives transcriptions, bundled as `Charter/texts.json`. Refresh after web text changes:

```bash
node export_bundle.mjs
```

That copies `texts.json` and both PDFs into the app target.

## Deep links

`charter://declaration/grievance-17`  
`charter://constitution/preamble`  
`charter://rights/1`  
`charter://later/11`
