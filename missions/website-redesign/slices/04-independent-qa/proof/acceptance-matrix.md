# QA acceptance matrix — OPR.99.0.1.4 (preflight, pre-build)

Author: review-qa@zero (claude-sonnet-5). Date: 2026-09-28. Updated 2026-09-28 05:10Z
(slice 03 now in-progress; refreshed stale refs per main-lead audit).
Status: **preflight only** — no candidate SHA has been assigned to QA yet, even though
implementation (slice 03) is in progress. This is the checklist I will run against the
actual `landing/` candidate once main-lead assigns the slice. Not a verdict. Do not treat
any row below as passed.

Sources: slice 01 `proof/DESIGN-BRIEF.md` (direction, viewports, must-stay, a11y/contrast),
slice 02 `proof/COPY-DECK.md` (28-row claims ledger, copy), slice 04 `SPEC.md`
(mini-requirements 1-4), README.md/PRODUCT.md (claims authority, though app source > README
per the claims ledger), `landing/test-site.mjs`, `landing/build.sh`. README's
"Daily routine"/"Reply drafting" labels were corrected to match app source at `cbb4073`
(2026-09-28 23:06 local) — the copy-deck's "README is stale" note in §5 below now predates
that fix and is tracked as historical, not current.

## 1. Visual compare vs approved mockup (desktop/mobile)

Reference captures: slice 01 `proof/mockup-desktop-{viewport,full}.png`,
`mockup-mobile-{viewport,full}.png`, `mockup-mobile-320-{viewport,full}.png`.

| # | Check | Reference spec | Evidence to capture |
| --- | --- | --- | --- |
| 1.1 | Desktop first viewport 1440×900 | Flap board ~210px tall, aria-hidden, sr-only `<h1>`; 5:6 two-column split below; install CTA + "Read the installer first" + Needs/Sorting/Cost list left; real `zero-panel.png` ~745px wide, top 408px, fictional-content caption right | `landing-desktop-1440-viewport.png` vs mockup |
| 1.2 | Mobile 390×844 | 3×10 tile board, full-width CTA ~424px, app image follows | `landing-mobile-390-viewport.png` vs mockup |
| 1.3 | Mobile 320 | No horizontal overflow, board rewraps (own composition per brief, not literal reflow) | `landing-mobile-320-viewport.png`, scripted overflow check |
| 1.4 | Color system | Signal-yellow `#FFC72C` ground, enamel-navy `#0A1F44` type, tickets-stock `#F6F1E4` for "Before you install"/"Questions" (approved refinement §7), navy install band between light sections | Screenshot + computed-style spot check |
| 1.5 | Typography | Archivo variable, condensed width for board/headings, normal width body; Geist Mono only in install command + label chip | Screenshot + computed font-family |
| 1.6 | Board content | "What stays" board uses **Archived** (copy-deck override of mockup's "Set aside"), rows paraphrase keep-policy.md defaults, labelled "Illustration... not a guarantee" | Text compare |
| 1.7 | Signature interaction | Headline tiles cycle/settle once <1s, left to right; static under `prefers-reduced-motion`; nothing else animates | Manual observe + reduced-motion media query test |
| 1.8 | Full-page scroll captures | No unapproved layout drift section to section vs mockup; note any deviation explicitly (spec requires "deviations noted", not zero-tolerance) | `landing-{desktop,mobile}-full.png` |

## 2. Keyboard / accessibility / motion (SPEC mini-req 2)

| # | Check | Reference | Evidence |
| --- | --- | --- | --- |
| 2.1 | Keyboard-only navigation | Tab reaches CTA, nav, FAQ disclosures, copy button in a sane order | Manual tab-through, note order |
| 2.2 | Focus visibility | Visible 3px focus rings, navy-on-yellow / yellow-on-navy-black per brief | Screenshot per focus state |
| 2.3 | Contrast (computed WCAG, brief §4 numbers) | navy/yellow 10.4:1, ink-soft/yellow 6.7:1, glyph-dim/board 6.2:1, glyph/flap 14.0:1, yellow/board 11.7:1, `#C9CFDC`/navy 10.4:1, navy/off-white 14.4:1, ink-soft/off-white 9.3:1 | Re-measure on built page, not just brief's claim |
| 2.4 | Reduced motion | `prefers-reduced-motion: reduce` shows static state, content visible without JS | DevTools emulate + JS-disabled load |
| 2.5 | Alt text | `zero-panel.png` has fictional-content alt/caption; other images have appropriate alt | Inspect DOM |
| 2.6 | Copy button (a11y contract) | ids `install-command`, `copy-command` (hidden until clipboard available), `copy-status` (live region); "Copied." / "copy it manually" messages; disabled while pending | Manual + `node --test landing/test-site.mjs` |
| 2.7 | Disclosures | FAQ uses native `<details>` | Inspect DOM |
| 2.8 | Narrow/wide viewport behavior | No horizontal scroll at 320-1440+; board tiles wrap as whole words, never mid-word | Scripted overflow check + visual |
| 2.9 | sr-only landmarks | Real `<h1>` present even though flap board is `aria-hidden` | Inspect DOM / accessibility tree |

## 3. Claims and routes audit (SPEC mini-req 3)

Full 28-row ledger in slice 02 `proof/COPY-DECK.md` §3. QA re-verifies against **repository
source**, not just the ledger's say-so (ledger authority order: app source > README >
install-zero.sh > privacy.html; PRODUCT.md not authoritative — same order I will use).

| # | Check | Evidence |
| --- | --- | --- |
| 3.1 | Every visitor-facing claim on the built page traces to source (spot-check all 28 ledger rows against actual repo files, not just trust the deck) | Row-by-row pass/fail table |
| 3.2 | Excluded claims stay excluded: no "once a day", "every thread", "Nothing leaves your account", metrics, logos, testimonials, adoption numbers, conversion claims | Full-text scan of built copy |
| 3.3 | Install routes: `/install` and `/install.sh` return 302 via nginx, script parses (`bash -n`), starts with `#!/usr/bin/env bash` | `landing/build.sh` output |
| 3.4 | Static routes: `/privacy.html`, `/terms.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `og.png`, unknown path 404 | `landing/build.sh` output |
| 3.5 | `node --test landing/test-site.mjs` green | Command output |
| 3.6 | Docker smoke (`landing/build.sh`) full pass | Command output |
| 3.7 | Copy-to-clipboard fallback behavior matches test-site.mjs contract | Test output + manual click |
| 3.8 | Warning appears **before** the install command (prior reviewer finding, must-stay) | Visual/DOM order check |
| 3.9 | macOS 26+, Apple Silicon, Gmail, Jev key requirements stated, undimmed, near the CTA | Visual + text compare |
| 3.10 | DESIGN.md rewritten to describe the *built* world, not the discarded charcoal/coral one (brief §6.3) | Diff review |
| 3.11 | Self-hosted Archivo (not Google Fonts CDN) in production, per build note | Network tab / asset check |
| 3.12 | Fonts/assets actually load (200s): Archivo, Geist Mono, panel image | `landing/build.sh` route checks (will need updating for Archivo if font filenames change) |

## 4. Known residue to watch for (carried from slices 01/02, historical — see cbb4073 note above)

- Copy deck's §5 note flagged README as stale on "Daily schedule"/"AI engine" vs app source
  ("Daily routine"/"Reply drafting"). **Corrected in `cbb4073`** — README now matches app
  source. QA confirms the built page also uses the current app-source terms, and treats the
  deck's note as historical context, not a live discrepancy.
- Mockup used Google Fonts for Archivo; production must self-host (build note, item 3.11
  above catches this).
- Copy is draft-quality-approved but layout tolerates ~±30% length variance (brief §5) — QA
  should not fail on minor length drift alone, only on layout breakage or overflow it causes.
- "Set aside" vs "Archived" naming conflict between slice 01 mockup and slice 02 copy deck:
  the deck instructs the builder to follow the deck (**Archived**). QA checks the *built page*
  matches the deck's instruction, not the mockup literally, on this one point.

## 5. Explicitly out of scope for this QA pass

- Production deployment / Dokploy (slice 05, mission lead).
- Inventing conversion-performance numbers (no analytics exist; SPEC forbids claiming
  automated tests equal visual acceptance).
- Any repair beyond what SPEC mini-req 1 allows ("have builder repair material differences
  and re-check once" — QA does not silently fix `landing/` itself).

## Next step

Wait for main-lead to assign OPR.99.0.1.4 with a candidate SHA. This is a shared local repo
with no push/pull; inspect the committed candidate SHA directly in place (`git show`/`git
diff` against it as needed), no network fetch. Then: run `landing/build.sh` and
`node --test landing/test-site.mjs`, capture desktop 1440 / mobile 390 / mobile 320
screenshots (real page, not mockup) via Aside, re-measure contrast on the built page, walk
the claims ledger against source, and produce PROOF.md with a pass/fail per requirement and
per-row evidence, dropped via `rig proof add OPR.99.0.1.4 ...`.
