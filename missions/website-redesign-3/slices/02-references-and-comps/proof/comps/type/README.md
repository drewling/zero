# Heading type: four options on real zero headlines

Owner feedback 2 asked for more legible heading type. This is the evidence behind the pick. **T3 is design.lead's recommendation and is not approved.** The owner gate goes through main-lead.

Open `specimen.html` from the comp server (`http://127.0.0.1:8941/type/specimen.html`, served from `proof/comps/`). Every option sets the same real strings: the hero H1, the Draft3 section headings, the button and tab labels, and one `first · fixed · file` ligature line.

| Option | Headings | Short UI labels (menu bar, titles, tabs, buttons) | x-height / em |
|---|---|---|---|
| P0 (current live and comps) | Pixelify Sans 600 | Pixelify Sans | 0.46 |
| T1 | ChicagoFLF | ChicagoFLF | 0.58 |
| T2 | Geist Pixel (Square, ELSH=1) | Geist Pixel | 0.53 |
| **T3 (recommended)** | **Geist 700, -0.03em** | **ChicagoFLF** | 0.53 / 0.58 |

## Findings

- **Legibility.** Page-level Tesseract proxy (share of heading and label strings read exactly): P0 0.30 at 320 and 0.35 at 390, against 0.926 for T1 and T3. At 1440, T3 scored best (0.866). At 390@1x, P0 misread "that" as "thot", "for" as "For" and "Restore all" as "Restoreall". The full list is in `ocr-errors.txt`.
- **Why T3 over T1.** ChicagoFLF carries the Mac identity at label size, where it's crisp. At 44–70px headline sizes it gets heavy and blocky, and it lacks `→`. Geist 700 headlines keep the page readable at a glance and match the body face already shipped. The one-bit character stays in the windows, labels and icons.
- **ffi and fi.** Pixelify draws "first" as "Arst" through its fi ligature (a live-site bug). Geist Pixel's liga also has an fi glyph. `kit.css` forces `font-variant-ligatures:none !important` everywhere. With ligatures off, T1, T2 and T3 read the letters of `first · fixed · file` correctly (the leftover OCR noise is the middle dot). P0 still reads as "First Fixed File": Pixelify's lowercase f looks like a capital F even without the ligature.
- **Missing glyphs.** None of the pixel candidates has `→`. ChiKareGo2 also lacks `·`. In T3 the one arrow (`Settings → Rules`) is set in Geist, so it renders from a real glyph, not a fallback.
- **Overflow.** 0px horizontal overflow at 320, 390, 1440 and 1920 for every option (`shots/`).

## Method and limits

- `ocr2.mjs` (page level) and `ocr3.mjs` (per element, `tesseract --psm 6`) in Chromium at 390@1x and 1440@2x. OCR is a proxy for human legibility, not a reading test. It punishes pixel faces for texture that people read fine, and it can't judge tone. Fresh readers and review-qa are the real test (slice 01 protocol).
- Chromium only for OCR. The page comps that use T3 pass the real-engine acceptance in Chromium and WebKit (`../../acceptance/pages-*.log`). Real Safari 26 and real devices are not verified.

## Licenses

- `kit/chicagoflf.woff2`: ChicagoFLF by Robin Casady, public domain, from the sakofchit/system.css repository.
- `kit/geist-pixel.woff2`: Geist Pixel by Vercel, SIL Open Font License 1.1, `kit/OFL-geist-pixel.txt`. It's here for option T2 only and isn't used by the page comps.
- Geist and Geist Mono are already in the kit (OFL).
- ChiKareGo2 was tested and rejected: it's CC-BY (it needs attribution on the page) and it lacks `·`. It isn't committed.
