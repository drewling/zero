# Slice 05 independent QA proof

**Candidate:** `c53bf919e2a94502fcc11d96ad96a52c1df60753` ("landing: redraw the hero app panel as one-bit HTML/CSS (slice 05)")

**Verdict: PASS**, with one process note (not a defect) below. No push or deploy performed; this QA is a prerequisite for advisor-lead's release decision only.

## Why this candidate, not the working tree

At QA time `landing/` in the shared working tree had uncommitted, in-progress edits to `site.css` and `test-site.mjs` beyond `c53bf91` (a `.zp-line` wrap/sizing tweak and a `@container` rule), and the diff grew between two checks in this session, meaning design-lead was actively iterating live. QA was therefore run against an isolated `git archive` of the exact committed SHA `c53bf91`, not the shared dirty tree, so this verdict is reproducible and not a moving target. If the uncommitted work is meant to ship, it needs its own commit and its own QA pass; it is not covered by this PASS.

## Requirement-mapped results

| Requirement (SPEC.md) | Check performed | Result |
| --- | --- | --- |
| Faithful structure: header (wordmark, account badges with counts, More menu) | Read `PanelView.swift` `TopBar`/`AccountDot`; compared to `.zp-head`/`.zp-mark`/`.zp-dots`/`.zp-more` in `index.html` | **Pass.** Wordmark with check glyph, two account badges with inbox counts (`TA 99+`, `LI 25`), overflow-menu dots present. |
| Tabs: Open loops, Accounts, Undo, Settings | Read `KeeperModel.swift` `enum Tab` titles | **Pass.** `.zp-tabs` lists all four in the exact real order and titles, with "Open loops" marked active (`.zp-on`), matching the real default tab. |
| Count, subline, "Across N accounts..." | Read `HeroCount` in `PanelView.swift` | **Pass.** `<strong>416</strong>` + "things still need you" + "Across 2 accounts. Tap any to open it in Gmail." — wording matches the real pluralized/singular pattern and the real helper copy verbatim. |
| Waiting-on-you rows: avatar, sender, subject, category tag, age, chevron | Read `LoopRowView.card` in `PanelView.swift`; compared to `.zp-rows li` markup | **Pass.** Each row has avatar-initials, bold sender, tag (only on rows that have one, matching the real conditional `if let cat = category`), subject line, chevron, and age. Tag vocabulary is exactly the two real ones from `lib/review_open_loops.py` line 123/127: "Needs reply" and "Action required" — no invented tag names. |
| Row actions: Reply, AI archive, Archive | Read `RowAction` calls at `PanelView.swift:582-590` | **Pass.** Icon order and semantics match: reply-arrow, sparkles ("AI archive"), archive-box, in that exact left-to-right order, matching the real `HStack` order. |
| Footer: "Tidies every inbox to only what needs you." and Run zero now | Read `ActionBar.statusText` and button label at `PanelView.swift:2941,2956` | **Pass.** Both strings are character-for-character identical to the real source, including the verb "Tidies" (not "Cleans" or similar). |
| No invented features; fictional names only | Structural diff against source; content review | **Pass.** No feature present in the redraw that isn't in `PanelView.swift`/`KeeperModel.swift` (no settings gear, no swipe hints, no toasts — appropriately, since this is a static decorative illustration, not a functional replica). All five names (Alex Rivera, Priya Sharma, Daniel Kim, Sarah Mitchell, James Carter, Emma Wilson) and subjects are plainly fictional/generic, not real people or real zero users. |
| Honest caption | Read `figcaption` in `index.html` | **Pass.** "zero's real layout, redrawn. Names and subjects are made up." — present verbatim, exactly as SPEC.md requires. |
| Works at 1440/390/320, no clipping/overflow | Real Chromium + WebKit renders (Playwright, not DOM-only assertions) against an isolated static server serving the exact-SHA archive | **Pass.** `document.documentElement.clientWidth === scrollWidth` at all three widths in both engines (320/390/1440). Panel `right` edge never exceeds the viewport (`overflowingPastViewport: false` at all 3×2 = 6 combinations). Zero page/console errors in either engine. |
| Row-level tag/name collision or clipping under fictional data | Custom per-row geometry check across 320/390/761/1024/1100/1280/1440 (own script, not reusing design-lead's) | **Pass.** At every width, tagged rows show no name/tag bounding-box overlap and the tag never overflows the row's right edge. Row 5 (index 5, no tag) renders 0-size only in the 761–1279px band, which is the documented "hide rows 5–6" behavior, not a bug. |
| Rows 5–6 hidden only 761–1279px | Row-count sweep at 320/390/760/761/1024/1100/1279/1280/1440 | **Pass.** 6/6 rows visible everywhere except 761–1279px inclusive, where exactly 4/6 are visible; 760px and 1280px (just outside the band) both show 6/6, confirming the boundary is exact, not off-by-one. |
| Caption clear of Trash cue, 761–1440px | Bounding-box overlap check, same sweep | **Pass.** `overlapCaptionTrash: false` at every tested width including the boundary widths. |
| Decorative a11y: aria-hidden + inert, sr-only summary, zero focusables | DOM assertions inside real Chromium and WebKit pages (not static regex) | **Pass.** `.zp` has `aria-hidden="true"` and the live DOM `inert` property is `true` in both engines at all three viewports. `focusablesInPanel` is `0` everywhere (no `a`/`button`/`input`/`[tabindex]` found inside `.zp`). The sr-only summary text is present and accurately describes count, accounts, row anatomy, tags, and the Run zero now button. |
| No motion / reduced motion | `getAnimations().length` and computed `animationName`/`transitionDuration` on `.zp` under `reducedMotion:'reduce'` context, both engines | **Pass.** `animCount: 0`, `animationName: "none"`, `transitionDuration: "0s"` in both Chromium and WebKit — the panel has no motion to reduce, consistent with SPEC.md's "keep it static." |
| Works without JS | `javaScriptEnabled: false` context, both engines, real navigation not an iframe | **Pass.** Panel present, all 6 rows present, non-zero rendered size (372×637 Chromium / 372×631 WebKit) with JS off. |
| Versioned stylesheet href (cache-bust) | DOM read of `link[rel=stylesheet]` | **Pass.** `/site.css?v=05` confirmed live in the rendered DOM, not just the HTML source, in both engines at all viewports. |
| `panel-cut.png` removed; `zero-panel.png` kept as og:image | HTTP probes against the built artifact | **Pass.** `/assets/panel-cut.png` → 404. `/assets/zero-panel.png` → 200. `build.sh`/`DESIGN.md` no longer reference the crop. |
| `node --test landing/test-site.mjs` | Ran independently against the isolated `c53bf91` archive (not the dirty working tree) | **Pass.** 7/7, including the new faithfulness test (`hero panel is a faithful, decorative one-bit redraw of the real Open loops panel`). |
| `bash landing/build.sh` (Docker/nginx) | Ran independently against the isolated `c53bf91` archive | **Pass.** Image built; homepage/privacy/terms/CSS/JS/all 4 fonts/`zero-panel.png`/unknown-path all correct; `/install` and `/install.sh` both 302; fetched install script (280 lines) parses. No container left running afterward. |

## Not verified (same boundary design-lead already disclosed)

- VoiceOver, Safari, and Firefox were not run. Chromium and WebKit (Playwright engines) were used here, which covers two of the three named engines design-lead asked about but not Safari-proper or Firefox.
- No formal axe/Lighthouse audit.
- The comp server at `127.0.0.1:8936` referenced in design-lead's message was not used; an independent isolated static server + Docker build were used instead so the result is reproducible without depending on design-lead's local process.

## Verdict

**PASS** for candidate `c53bf91` against every SPEC.md mini-requirement, independently re-verified (not re-stating design-lead's own PROGRESS.md numbers) with fresh Chromium+WebKit renders, a fresh Docker/nginx build, and direct source comparison against `PanelView.swift`/`KeeperModel.swift`/`lib/review_open_loops.py`. The uncommitted `site.css`/`test-site.mjs` changes observed live in the working tree during QA are outside this verdict's scope and were not evaluated; if they are meant to ship they need a new commit and a new QA pass.
