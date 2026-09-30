# Independent adversarial review: Page B proposal at 50bf121

**Reviewer:** review-qa@zero (independent seat, no co-authoring). **Object reviewed:** `comps/page-b/index.html` + `comps/kit/*` at frozen SHA `50bf1213e06975ba8897400ef57ac8f1c2e07cfb` (HEAD, working tree clean at review time). **Method:** two adversarial passes (sceptical-stranger, design-critic) against `SPEC.md` Boundaries, `PRODUCT.md`, and the real shipped source (`bin/zero`, `install-zero.sh`, `lib/keeper_server.py`, the public TypeSafe pricing page). This is findings only — no fixes, no copy edits, no `landing/` changes, no push, no deploy.

**Scope note:** this is a comp-stage review of frozen Page B (mission gate: design-lead's freeze handoff), not the slice-05 built-page checklist (cold-reader test on the live build, Docker packaging, Lighthouse) which applies once `03-build-structure`/`04-motion-and-polish` produce a real `landing/` SHA. Findings below are about the proposal as frozen, scoped to what a comp can actually prove.

## What I independently reproduced (not just trusted)

1. **Chromium acceptance, rerun clean**: `146 PASS, 0 FAIL` — matches design-lead's report exactly. Log: `proof/pages-chromium-independent.log`.
2. **WebKit acceptance, rerun clean** (pinned build `webkit-2336`, per design-lead's instruction to avoid the default Playwright-pinned revision mismatch): `142 PASS, 0 FAIL` — matches exactly. Log: `proof/pages-webkit-independent.log`.
3. Served via design-lead's `acceptance/serve.py` (threaded, 128-backlog), not plain `http.server`, as instructed.
4. **Independent screenshots** captured myself (not reused from design-lead): Chromium + WebKit, full page at 320/390/1440/1920, no-JS at 390/1440, `prefers-reduced-motion:reduce` at 390/1440 — 16 images total in `proof/shots/` (a representative subset copied; full set retained in review session).
5. **Programmatic dither/stripe-background text scan** across all 4 widths: only match is the intentionally `sr-only` hero description (never visually rendered) — zero visible text sits on a dither or stripe background. Confirms the SPEC boundary "no text on stripes/dither."
6. **Split-band vertical centring measured directly** (`getBoundingClientRect` on `.txt`/`.field`/`.obj` at 1440): both `split-r` (`how-band`) and `split-l` (`undo`) bands show `.txt` vertically centred against the field, closing the `IMPECCABLE-CRITIQUE-pages.md` "empty halves" priority issue.
7. **Re-probed the public install.sh redirect myself**, 3 separate attempts, all clean `302 → 200` to `github.com/drewling/zero/blob/master/macapp/install-zero.sh`. Design-lead's copywriter run hit a transient `429` (GitHub rate limit) on this same edge and flagged it as "re-probe, don't assume" — confirmed it is a transient external rate-limit, not a real broken redirect. Also checked `/install` (→ raw.githubusercontent, 302→200), `/privacy.html` (200), `/terms.html` (200).
8. **AGPL-3.0 license claim** checked against the actual repository `LICENSE` file — verified true (AGPLv3 text present).
9. **No-schedule-promise claim** checked by grepping the full rendered markup for daily/automatic/schedule language: the only match is "Drafts never send automatically" (a true negative claim, consistent with `PRODUCT.md`'s "not an auto-replier"). No conflicting scheduling promise exists on the page, matching `schedule-and-price-evidence.md`'s requirement.
10. **Hero markup/CSS fidelity vs the approved standalone `hero-b/index.html` comp**: byte-identical except the one deliberate root-relative → canonical-URL link swap that `SELECTED-B-COPY.md` explicitly calls for. No silent hero drift during page assembly.
11. Verified `page-a` (archived) is untouched since `39aa729` and its `ARCHIVED.md` accurately documents why/where to check it out.

## Sceptical-stranger pass (confusion / credibility / overreach)

### Finding 1 — Trash icon in the hero contradicts "nothing is deleted," with no visible cue that it's empty
**Severity: Medium.** The hero shows an `Auto-Archived` folder icon (filled state, labelled) directly beside a `Trash` icon rendered with the same weight, same fill treatment, and no visual distinction for "empty." The only place the page discloses "Trash stays empty" is an `sr-only` paragraph never rendered to sighted visitors. A fresh third-party reader independently exercising the exact frozen SHA (`readers/after-b-tightened/matched-1.answer.md`, `50bf121`, ranked this their #1 priority fix) flagged this as directly undermining the page's core reversibility claim ("Undo any archive. Nothing is deleted."), and I independently confirmed by zoomed pixel inspection (`proof/shots/hero-trash-icon-zoom.png`) that there is no empty/full visual state on the Trash icon at any width — it's a static icon, not a stateful one like the folder (which does have `f-full`/`f-empty` SVG swap logic in CSS). This is exactly the kind of self-contradiction the sceptical-stranger pass exists to catch, and it's evidence-backed by an independent reader, not just my own read.
**Evidence:** `proof/shots/hero-trash-icon-zoom.png`; markup at `page-b/index.html:189-190`; CSS `svg.px.f-empty{display:none}` only applies to `.folder`, never `.trash`, in `kit/page.css`/inline styles.
**Suggested fix direction (not prescribed):** either give Trash an explicit empty-state affordance (outline-only/greyed, matching the folder's stateful pattern) or drop the Trash icon from the hero illustration entirely, since it isn't load-bearing to the "sort into a dated folder" story and only invites the "wait, is something being deleted?" reading.

### Finding 2 — "Free, open-source app" sits directly beside a paid per-token rate, with no real-world cost anchor
**Severity: Low-Medium.** The ledger row juxtaposes "Sorting cost. Your Jev key, billed by TypeSafe. Jev 1.13: $0.042 per million input tokens... Free, open-source app (AGPL-3.0)" in one paragraph. I verified the $0.042/M rate is accurate against the live source (`https://docs.typesafe.ai/models`, checked independently) and that `schedule-and-price-evidence.md` explicitly prohibits inventing a per-inbox/month estimate — so the copy is *correct* and appropriately conservative. But two of three independent fresh readers on this exact frozen SHA still flagged the "free ... vs metered" juxtaposition as confusing ("the app is free, but running it isn't really free"). This is a disclosed, already-known-open item (design-lead's addendum explicitly says "All three ask for a real-world cost... Treat these as open, not fixed"), so I am not counting it as a new finding requiring action before this gate — flagging it here only because the sceptical-stranger pass is supposed to independently confirm disclosed gaps, not just take them on faith. Confirmed: still present, still unresolved, correctly not fabricated around.

### Finding 3 — Non-finding, verified: "Read the installer first" / curl\|bash tension is accurately disclosed, not overreach
Two of three fresh readers questioned "zero is a Mac app" framing against a Terminal `curl | bash` installer with no `.dmg`. I checked the real `install-zero.sh` source: it does install prerequisites (Homebrew, Python, Node, gws) before installing `zero.app`, exactly as the page's "May add Homebrew, Python, Node and Google Workspace CLI" line states, and the hero explicitly offers "Read the installer first" as a secondary link before the primary CTA. This is a legitimate product characteristic being disclosed honestly, not a copy overreach — no finding, but worth naming since a reader raised it and PRODUCT.md's own "Setup, the way it should feel" section frames `npx zero init` as *aspirational*, not what ships today. The page does **not** claim `npx zero init` exists; it correctly matches the real installer. Confirmed by direct source read, not assumption.

### Finding 4 — Non-finding, verified: schedule claims stay within Boundaries
Checked the full rendered page text against `schedule-and-price-evidence.md`'s source trace (`bin/zero:169-229`, `lib/keeper_server.py:1890-1897`, tooltip in `PanelView.swift:2947` that overclaims "runs automatically each morning"). The page makes no daily/automatic-run claim anywhere; "Run zero now" is presented as an immediate manual action, consistent with the conditional, not-installed-by-default reality of the launch agent. No overreach found.

## Design-critic pass (legibility / layout / contrast / motion / one-bit style)

### Finding 5 — Confirmed fixed: split-band empty halves (prior IMPECCABLE-CRITIQUE priority issue #1)
Measured directly via `getBoundingClientRect` rather than trusting the critique doc's claim of a fix: `.txt` in both `split-r` and `split-l` bands is vertically centred against its `.field` counterpart at 1440 (`how-band`: field 1951-2680 vs txt 2114-2516, roughly centred; `undo`: field 2682-3364 vs txt 2846-3200, roughly centred). No longer reads as ~55% empty. **No finding — closed.**

### Finding 6 — Confirmed fixed: Rules editor mid-clause wrap (prior priority issue #4)
Zoomed pixel inspection of the rendered Rules pane at 1440 shows "Cold outreach, sales, prospecting, pitches, even when the sender uses a real human name and I have never replied to them" wrapping cleanly across 2 lines with no mid-word or mid-clause ragged break. **No finding — closed.**

### Finding 7 — Confirmed: no text sits on a dither/stripe background at any required width
Programmatic check across 320/390/1440/1920 (leaf-element background walk) found zero visibly-rendered text on a dithered or striped background; all labels (`Trash`, folder label, `Illustration.` captions, footer brand, draft flag) sit on solid black or solid white boxes with full contrast. **No finding — closed**, matches SPEC Boundaries and the owner's original stripe-legibility complaint.

### Finding 8 — Confirmed: heading legibility holds at all 4 required widths
`h1`/`h2` render in Geist (not Pixelify/ChicagoFLF), matching `page.css`'s documented T3 type decision, which the design brief's own OCR test (0.93 vs 0.30-0.35 for the old Pixelify heading face) already established. Visually re-confirmed at 320/390/1440/1920 in my independently captured screenshots: headline stays crisp, no clipping, no overflow (also confirmed by the acceptance suite's `no clipped text` / `no horizontal overflow` checks at all 6 tested widths including 2560, all passing in my rerun). **No finding.**

### Finding 9 — Motion: reduced-motion and no-JS both genuinely settle to the complete final frame
Independently captured `prefers-reduced-motion: reduce` and `javaScriptEnabled: false` contexts at 390 and 1440 (not reused from design-lead). Visual inspection confirms: full "Before you install" ledger, complete Rules text, complete Undo list with `Restore all`, and the Terminal command are all present and unclipped in both states — nothing loops, nothing is left mid-animation, no stray `lt-*` partial-state classes visible. Cross-checked against the acceptance log's own `reduced-motion == final frame` / `no-JS == final frame` assertions, which I independently reran and confirmed passing. **No finding.**

### Finding 10 — Motion: stepped animation stays well clear of flash/strobe thresholds
Read `kit/motion.js` directly: row-select inversions step one row at a time with a 70ms `wait` between each (8 rows over ~560ms total), not a simultaneous full-field flash; drag-outline stepping runs over 7 steps at 80ms each. No single-frame full-viewport inversion occurs anywhere in the frame list. Well under the WCAG 2.3.1 three-flashes-per-second threshold. **No finding.**

### Finding 11 — One-bit style used as communication, not decoration, in the sections that matter most
The Undo and Settings/Rules objects are zero's real UI chrome carrying real accessible text (confirmed via the acceptance suite's word-count assertion and my own DOM read: these are *not* `aria-hidden`, unlike the hero's illustrative popover/inbox, which correctly *is* hidden with an `sr-only` substitute). The reversibility claim is proven by an actual Undo list with a real "Restore all" control, not merely illustrated. This matches the design brief's own strength note ("the Undo rows and the balloon *are* the reversibility claim") — independently re-verified, not just repeated. **No finding.**

## Known-open items probed (not counted as new findings, per design-lead's disclosure)

- **Public edge/canonical link check:** independently re-probed; confirmed transient (see "What I independently reproduced" #7). Not a defect.
- **Tightened-B fresh reader results:** read in full (`TIGHTENED-B-READERS.md`, 3 fresh sessions on this exact SHA). Confirmed genuine (untracked but present, consistent with design-lead's "addendum, frozen tree unchanged" framing; `git diff` against HEAD shows zero changes to `comps/`). Findability improved narrowly (a single +1), readiness did not improve — I am treating this as the mission's own honest self-report, not something for me to re-litigate; Finding 1 above is the one item from those reads I independently re-verified as a real, currently-uncounted visual defect.
- **WebKit build identity (Playwright 2336, not real Safari):** disclosed limitation, out of scope for a comp-stage review; noted, not treated as a finding.
- **Clipboard tested via stub, not real OS clipboard:** verified the stub exercises the actual production `navigator.clipboard` code path in `kit/sections.js` (feature-detected, hidden when unavailable), which is the standard way to test this browser API without OS-level automation. Legitimate test method, not a gap I'm counting against this gate.
- **Real Safari/device testing, schedule promise, development-motion sandbox separateness:** disclosed, not independently checkable at comp stage, not counted.

## Summary for design-lead

- **1 new finding requiring a decision before re-freeze:** the hero Trash icon (Finding 1) reads as a self-contradiction of the page's central "nothing is deleted" promise, independently confirmed by a fresh reader and by my own pixel-level inspection. This is squarely a design/illustration fix (add an empty-state affordance or remove the icon), not a copy fix — copywriter's job is done here; this is design's call.
- **1 disclosed-and-confirmed-still-open item**, not a new finding: the free-app/paid-metering juxtaposition (Finding 2). Already flagged by 2/3 fresh readers and correctly not being papered over with an invented cost estimate. Owner-level decision, not mine to resolve.
- **2 prior priority issues confirmed closed** by direct measurement (empty split-band halves, Rules mid-clause wrap).
- **Everything else I checked** — dither/stripe text, heading legibility at all widths, reduced-motion/no-JS completeness, flash safety, keyboard order/focus/clipboard states, canonical link health, license claim, schedule-claim boundary compliance, hero fidelity vs the approved standalone comp — held up under independent reproduction.
- Both engines' acceptance suites reproduce clean at the exact counts design-lead reported (146/0 Chromium, 142/0 WebKit). No discrepancy found.

No `landing/` files touched. No fixes applied. Findings only.
