# Slice 05 independent QA proof

**Candidates verified:**
- `c53bf919e2a94502fcc11d96ad96a52c1df60753` — original panel redraw (slice 05). **PASS**, see Pass 1 below.
- `c32f10d611cc6f6fae12acb1b9d2090431d3897a` (HEAD) — adds design-lead's sender-name-truncation fix (advisor-lead finding at 16:38Z: "Sarah Mit..." clipped at 1440). **PASS**, see Pass 2 below.

**Verdict: PASS on HEAD (`c32f10d`).** No push or deploy performed; this QA is a prerequisite for advisor-lead's release decision only.

## Process note on how these two commits relate (not a defect, but worth recording)

Pass 1 QA'd an isolated `git archive` of `c53bf91` because the shared working tree had uncommitted, actively-changing `site.css`/`test-site.mjs` edits at the time (design-lead iterating live on the truncation fix). After Pass 1's `PROOF.md` was written, `git commit` (run without a pathspec) on the new proof files accidentally also picked up those then-uncommitted `site.css`/`test-site.mjs`/`PROGRESS.md`/shot changes from the shared tree, bundling design-lead's truncation fix into the same commit (`c32f10d`) as the QA proof. This was flagged to design-lead, who confirmed the fix's contents and asked for a fresh PASS/FAIL specifically on `c32f10d`. Pass 2 below is that independent re-verification, run the same way as Pass 1: an isolated `git archive` of the exact commit, not the live working tree.

## Pass 1: `c53bf91` requirement-mapped results

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

## Pass 2: `c32f10d` (HEAD) requirement-mapped results — the sender-name-truncation fix

CSS diff between `c53bf91` and `c32f10d` (`landing/site.css`): row gap/padding tightened 1-2px, `.zp-line` now `flex-wrap:wrap` instead of nowrap, `.zp-line b` drops `overflow:hidden`/`text-overflow:ellipsis`/`white-space:nowrap` in favor of `max-width:100%`, `.zp-tag` font shrinks 10px→9.5px with tighter padding, and a new `@container (max-width:260px)` step shrinks the row avatar/name at the narrowest desktop panel widths. `landing/test-site.mjs` gained one new assertion that the `.zp-line b` rule has no `ellipsis`/`nowrap`/`overflow:hidden`. Re-verified independently against a fresh `git archive` of `c32f10d` (HEAD) on its own isolated static server, not reusing the Pass 1 server or archive.

| Requirement | Check performed | Result |
| --- | --- | --- |
| No sender name ever truncated, 1440/1366/1280/1180/1100/1024/900/800/761/760/390/320, both engines | Custom Playwright script reading `.zp-line b` computed style + rendered text for every row at all 12 widths × 2 engines (24 combinations) | **Pass.** 0 ellipsis characters in any rendered name, 0 instances of `text-overflow:ellipsis` or `white-space:nowrap` still computed, 0 names whose right edge exceeds the row's right edge. `Sarah Mitchell` (the specific reported defect) renders in full at 1440 in both engines. |
| Tag wraps under name only when both don't fit | Same script, bounding-box check `tag.top >= name.bottom - 1` | **Pass.** Confirmed wrap-under behavior at narrow widths where applicable; not spuriously wrapping at wide widths where both fit on one line. |
| Regression: no overflow, a11y, reduced motion, no-JS still hold after the CSS tightening | Reran the full Pass 1 Playwright regression script against the new archive, both engines, 320/390/1440 | **Pass.** `clientWidth === scrollWidth` at all 6 combinations, `aria-hidden="true"` + `inert === true` + `focusablesInPanel: 0` at all 6, sr-only summary intact, `animCount: 0` under reduced motion both engines, no-JS renders 6/6 rows both engines, `/site.css?v=05` href confirmed live. Zero page/console errors. |
| Row-level tag/name overlap re-check after tighter gaps | Reran the Pass 1 per-row geometry script against the new archive | **Pass.** 0 overlaps and 0 tag-row overflows across 28 tagged-row checks (7 widths × up to 4 tagged rows), i.e. the 1-2px gap tightening did not introduce a new collision. |
| Caption/Trash clearance and 761-1279px row-hiding band unaffected | Reran the Pass 1 width-sweep script against the new archive | **Pass.** `overlapCaptionTrash: false` at every tested width (320/390/760/761/1024/1100/1279/1280/1440); row-hiding band still exactly 761-1279px inclusive (4/6 visible), 760 and 1280 both 6/6. Matches design-lead's own reported 819-821 (caption) vs 845 (Trash) gap direction; independent measurement at 1440 gives panel bottom 747 / Trash top 845. |
| `node --test landing/test-site.mjs` | Ran independently against the isolated `c32f10d` archive | **Pass.** 7/7, including the new no-ellipsis/no-nowrap assertion on `.zp-line b`. |
| `bash landing/build.sh` (Docker/nginx) | Ran independently against the isolated `c32f10d` archive | **Pass.** Full pass, same checks as Pass 1. No container left running afterward; QA-only image tags removed after the check. |

## Direct before/after comparison (not just inspecting the fixed state)

The Pass 2 checks above only inspected `c32f10d` in isolation and inferred the defect was gone from the absence of clipping symptoms. To confirm the fix is an actual improvement rather than just a different-looking state, `c53bf91` and `c32f10d` were served simultaneously on two separate isolated ports from two separate `git archive` checkouts, and the exact same row (`Sarah Mitchell`, the row advisor-lead flagged) was measured at 1440px in the same browser session (script: `before-after-compare.mjs`, raw output: `before-after-result.json`).

| | `c53bf91` (before) | `c32f10d` (after) |
| --- | --- | --- |
| `text-overflow` | `ellipsis` | `clip` (harmless, nothing overflows) |
| `white-space` | `nowrap` | `normal` |
| `scrollWidth > clientWidth` (the actual DOM clipping signal) | **`true`** — the box's content is wider than its box, which is what `ellipsis` was hiding | `false` — no clipping |

This confirms the pre-fix commit had the real, DOM-measurable clipping condition (not just a visual impression), and the post-fix commit does not. A regression sweep across the same row indices at 1440/1024/761/390/320 comparing before vs. after found **0 rows where the after-state clips and the before-state didn't** — the fix does not trade the name-truncation bug for a new clipping bug elsewhere.

## Not verified (same boundary design-lead already disclosed)

- VoiceOver, Safari, and Firefox were not run. Chromium and WebKit (Playwright engines) were used here, which covers two of the three named engines design-lead asked about but not Safari-proper or Firefox.
- No formal axe/Lighthouse audit.
- The comp server at `127.0.0.1:8936` referenced in design-lead's message was not used; an independent isolated static server + Docker build were used instead so the result is reproducible without depending on design-lead's local process.

## Verdict

**PASS on `c32f10d` (HEAD)**, superseding the Pass 1 `c53bf91`-only verdict below. Independently re-verified (not re-stating design-lead's own PROGRESS.md numbers) with fresh Chromium+WebKit renders, a fresh Docker/nginx build, and direct source comparison against `PanelView.swift`/`KeeperModel.swift`/`lib/review_open_loops.py`, plus a targeted re-check of the sender-name-truncation fix at all 12 widths design-lead specified. This is the SHA design-lead is forwarding to advisor-lead for release.

Pass 1 verdict (for the record): **PASS** for candidate `c53bf91` against every SPEC.md mini-requirement, independently re-verified with fresh Chromium+WebKit renders, a fresh Docker/nginx build, and direct source comparison. At the time, the uncommitted `site.css`/`test-site.mjs` changes observed live in the working tree were outside that verdict's scope. Those changes are now committed as part of `c32f10d` and are covered by the Pass 2 verdict above.
