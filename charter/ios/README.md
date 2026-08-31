# Charter for iPhone

A native SwiftUI app. Same three founding texts as the web app, plus the whole PDF library (every book, light and dark), offline, share, and dark/light. Not a Bible app.

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

Requires Xcode 15+ and iOS 17. iPhone and iPad.

## What it includes

- Home table of the Declaration, Constitution, and Bill of Rights
- One bite per screen, swipe or Next / Prev
- Contents sheet
- Copy and the system share sheet (`charter://declaration/grievance-17`)
- Later amendments XI–XXVII
- The whole library in-app (Charter, Declaration, Constitution, Bill of Rights + later amendments × light/dark, PDFKit)
- Theme: System / Light / Dark
- Continue where you left off
- Footer: Created by Christ Supply, [Support Here](https://christ.supply/support-us)

Texts are the National Archives transcriptions, bundled as `Charter/texts.json`. Refresh after web text changes:

```bash
node export_bundle.mjs
```

That copies `texts.json` and all eight PDFs into the app target.

## Deep links

Share includes the public web URL and the app URL:

`https://liberatedluis.github.io/skills-introduction-to-github/charter/#/declaration/grievance-17`  
`charter://declaration/grievance-17`

Also: `charter://constitution/preamble` · `charter://rights/1` · `charter://later/11`
