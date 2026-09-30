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

---

## Pass 2 — independent re-check of follow-up SHA `65463b8` (2026-09-30)

**Object reviewed:** `65463b8` ("Render Draft5 privacy boundary, port motion race fix, update proposal for re-check"), one follow-up commit on top of the still-unchanged freeze `50bf121`. This is a lighter confirmation pass against design-lead's specific re-check list, not a full redo of pass 1's 11 checks + 11 findings.

**First, confirmed the freeze itself is untouched:** `git diff 50bf121..65463b8 -- comps/page-a comps/hero-b` is empty. The frozen hero and archived page A are byte-identical to what I reviewed in pass 1. Only `page-b`, `kit/motion.js`/`page.css`/`build-pages.py`/`sections.js`, the acceptance suite, the proposal page, docs, and evidence artifacts changed.

### Re-check 1 — Draft5 privacy boundary: rendered, correct, not dithered ✅
Read the raw `page-b/index.html` diff directly. Confirmed:
- Old line **"No zero server receives your email."** is fully absent from the markup (`grep` for the exact string returns nothing) — not just visually hidden.
- New line renders as its own `<p class="bound">` between the two outgoing-data rows (`Sorting data.`, `Optional drafts.`) and the `Sorting cost.` row, exactly as claimed — confirmed by DOM order in the HTML source, not just the acceptance suite's own assertion.
- CSS (`.ledger-b .info .bound`) sits on `var(--paper)` (solid white), bordered top/bottom, **no `--dither-25` background** — checked directly against the file's own dither-background declarations used elsewhere (`.ledger-b .info .row.out`), confirming the boundary statement is deliberately kept off the dither pattern, consistent with the one-bit "text on flat paper only" rule I verified in pass 1.
- Visually re-confirmed with my own fresh screenshots at 1440 and 390 (`proof/shots-pass2/pass2-ledger-{1440,390}.png`): the statement renders as a solid bordered box, full width of the info window at both sizes, directly under the recipient pair and above cost — matches the proposal page's own screenshot and description.
- Full-width claim independently true at both captured widths (box spans the whole `.info` window at 1440 and the single-column layout at 390 — no truncation, no overflow).

### Re-check 2 — Ledger lede line removed, no dangling layout gap ✅
Confirmed the `<p>Read connected Gmail in Gmail or Apple Mail.</p>` line is deleted from the `#install` section's `.txt` block (the new grid class `no-lede` is on the section, though I found no distinct CSS rule keyed to `no-lede` — the removal works because `.ledger .txt` is a 2-column grid and simply drops the second grid item without leaving a visible gap, which I visually confirmed in both screenshots: no empty box, no orphaned whitespace under the heading). Word budget claim (550/550, hero unchanged at 104) is consistent with `SELECTED-B-COPY.md`'s own accounting, which I did not independently recount word-by-word (out of scope for this lighter pass) but which the acceptance suite's own rendered-word-count assertion (part of the 148/144 rerun below) independently checks and passed.

### Re-check 3 — Motion race fix: present, logic matches the described fix ✅
Read the actual `kit/motion.js` diff line by line (not just trusted the changelog description). Confirmed the described change is real:
- `arm()` now calls `io.observe(root)` itself (previously `io.observe` was called unconditionally at the end of the setup function, before arming) — this closes the race where the play-observer could fire before the section had a chance to decide "already visible at first sight."
- Initial-sight decision is now made **synchronously**, before any observer is attached, using `getBoundingClientRect()` + a `location.hash` anchor-target check, replacing the old async-only `pre` IntersectionObserver-based decision. This directly matches design-lead's description ("io.observe only after arm, sync initial-sight check").
- A `started` guard was added to the `pre` observer callback to prevent a stale pre-observer delivery from re-triggering after the section has already been marked `seen`.
- This is a real, comprehensible fix for the described race, not just a description with no matching code change.

### Re-check 4 — New acceptance test 5b2 validates the actual race scenario ✅
Read the new `pages.mjs` test block directly: it scrolls the target ledger section into view via a `DOMContentLoaded` listener injected *before* `motion.js` runs (so the scroll can race the observer's first callback), then asserts the section reaches `data-mode="done"` (fully played, not skipped/stuck armed) with all rows visible. This is a legitimate regression test for the exact race described, not a superficial pass-through check.

### Re-check 5 — Proposal page (`comps/proposal/index.html`): scores table, Trash mock, evidence numbers all accurate ✅
Read the file directly (not just design-lead's description):
- `#readers` section has the 3×3 reader score table (rejected baseline / old B / tightened B, R1-R3), matches `TIGHTENED-B-READERS.md`'s numbers I independently reviewed in pass 1's addendum check.
- `#trash` section is headed **"Review-qa's one finding: the hero's Trash"** — correctly attributes the finding to me, includes a `trash-keep` (as-approved) vs `trash-drop` (proposed removal) side-by-side mock, and explicitly labels it **"mock, not built"** / "The mock removes the icon in a live browser. It isn't built into the page." I confirmed this is true: the Trash icon fix is genuinely **not** present in the actual `page-b/index.html` (see Re-check 6) — the proposal page is honestly describing a mockup for Tayo's decision, not silently shipping the fix while claiming it's still open.
- `#evidence` table states "Chromium 148/0, WebKit 144/0" for the privacy-fix commit — matches my own independent rerun exactly (see Re-check 7).

### Re-check 6 — Trash owner-gate: confirmed genuinely still unfixed ✅
Independently grepped the actual rendered `page-b/index.html` and `kit/page.css`/inline styles for `f-full`/`f-empty` (the folder's stateful empty/full swap mechanism I found in pass 1). Confirmed: the folder icon (`Auto-Archived` label) still has both `f-full` and `f-empty` SVG variants with CSS-driven visibility swap (`.lt-5 .folder:not(.got) svg.px.f-full{display:none}` / `f-empty{display:block}`). The Trash icon (line 190) still has **only one static `<svg>`**, no `f-full`/`f-empty` classes, no swap logic — unchanged from pass 1. This is a genuine owner-gated hold, not a silent fix mislabeled as pending. Matches design-lead's own framing ("OWNER GATE, unchanged, awaiting Tayo via main-lead").

### Re-check 7 — Acceptance suite independently reproduces 148/0 and 144/0 ✅
Reran from scratch on `65463b8` (fresh comp server on port 8944 via `serve.py`, not reused from pass 1):
- **Chromium: 148 PASS, 0 FAIL** — matches design-lead's claim exactly. Confirmed zero `FAIL` lines in the raw log (`grep -c "^FAIL"` → 0), not just trusting the summary line. New test 5b2 (`scroll before the first observer callback still plays the ledger beat to done`) passed for both `page-a` and `page-b`, including the `page-b` case with 6 visible rows (the new privacy-boundary paragraph counted as a row).
- **WebKit** (pinned build `webkit-2336`, same as pass 1): **144 PASS, 0 FAIL** — matches exactly, same zero-FAIL raw-log confirmation.
- Logs: `proof/acceptance-pass2/pages-{chromium,webkit}-pass2-independent.log`.

## Pass 2 summary for design-lead

All 6 re-check items independently verified true, with fresh evidence (not reused from pass 1 or trusted from the addendum message):
1. Draft5 privacy boundary — rendered correctly, full-width, not dithered, old line genuinely gone.
2. Ledger lede removal — clean, no layout gap.
3. Motion race fix — real code change matching the described fix, not just a changelog entry.
4. New regression test (5b2) — a legitimate test of the actual race, not superficial.
5. Proposal page — accurate, honestly labels the Trash mock as "not built," correctly attributes the finding to review-qa.
6. Trash owner-gate — confirmed genuinely untouched, correctly still deferred to Tayo, not silently patched around.
7. Acceptance — 148/0 Chromium, 144/0 WebKit independently reproduced, zero hidden FAILs.

**No new findings from this re-check.** The one open item from pass 1 (hero Trash icon) remains correctly unresolved and owner-gated — this commit does not attempt to fix it, only proposes a mock for Tayo's decision, which is the right scope. Page A and hero-B remain untouched. No `landing/` files touched. No fixes applied by this seat.

---

## Finding 1 status: CLOSED, owner-accepted (2026-09-30)

Tayo (via advisor-lead, relayed by main-lead 02:30Z) decided to **keep** the hero Trash icon as approved, declining the drop-it mock proposed in `comps/proposal/index.html#trash`. Finding 1 (hero Trash icon lacks an empty/full visual state, contradicting "nothing is deleted") is closed as an owner-accepted risk, not a defect requiring further design work. No code change was made in response to this finding, and none is expected. This is the correct terminal state for Finding 1: raised, evidenced, escalated to the owner via design-lead's proposal, decided.

---

## Pass 3 — final scoped re-check of frozen SHA `1ad99b3` (2026-09-30)

**Object reviewed:** `1ad99b34198d01c59e7d9fe52112b0526fd557b8`, the final frozen page B, one commit after `65463b8`. Design-lead's stated scope: only the Draft6 Sorting-cost row (source `SELECTED-B-COPY.md@3088502`), the draft flag, recaptured shots, and the proposal record. Main-lead flagged this as time-sensitive since slice 03 build is releasing in parallel against this same SHA — kept this pass narrow and fast, scoped strictly to what changed, not a redo of pass 1/2.

### Re-check A — Diff scope genuinely limited to cost row + flag + proposal ✅
`git diff 65463b8..1ad99b3 -- comps/page-a comps/hero-a comps/hero-b comps/hero-c comps/kit/sections.js comps/kit/motion.js comps/kit/page.css` is empty — confirmed myself, not trusted from the message. Hero, Trash, page A, section behavior, and motion are byte-identical to what pass 1/2 already reviewed. The only change in `page-b/index.html` itself is two lines: the `Sorting cost.` row text and the `draft-flag` caption (`Draft4` → `Draft6`, `not approved` → `not the live site`).

### Re-check B — Rendered cost row matches COPY-B at `3088502` exactly ✅
Diffed the rendered HTML row against `git show 3088502:.../SELECTED-B-COPY.md`'s `**Sorting cost.**` line word-for-word: *"TypeSafe-billed Jev key. Cost depends on how many emails you sort. Jev 1.13: $0.042/million input tokens, outputs free (2026-09-30). [Pricing](...). Free, open-source app (AGPL-3.0)."* — identical, including the exact tariff format, the dating, and the shortened "Pricing" link label. No monthly figure or worked example was invented, consistent with the source note that no measured token-count data was supplied.

### Re-check C — Word count 550 confirmed via the canonical counter script ✅
Ran `count-section-drafts.mjs` directly (not a manual regex/shell word-split, which gave a different, wrong count on a first naive attempt) against the current `SELECTED-B-COPY.md`: `authoredTotal: 550`, matching design-lead's claim exactly. This is the same tool the mission's own tests use, so it's the correct ground truth rather than a re-derived approximation.

### Re-check D — Acceptance suite independently reproduces 148/0 Chromium, 144/0 WebKit ✅
Fresh comp server (port 8945, `serve.py`, not reused from pass 2), fresh Playwright rerun on `1ad99b3`: **Chromium 148 PASS, 0 FAIL**; **WebKit 144 PASS, 0 FAIL** (pinned build `webkit-2336`) — exact match. Confirmed zero `FAIL` lines in the raw logs directly (`grep -c "^FAIL"` → 0 both engines), not just the summary line. The ledger-order/privacy-boundary assertion from pass 2 still passes unchanged. Logs: `proof/acceptance-pass3/pages-{chromium,webkit}-pass3-independent.log`.

### Re-check E — Proposal page: no overflow, no broken images at 320/390/1440/1920 ✅
Independently scripted a Playwright check against the actual `proposal/index.html` (not covered by `pages.mjs`, which only checks page-a/page-b) at all 4 required widths: zero horizontal overflow at any width. A first pass without a full-page scroll showed 22 apparently-"broken" `loading="lazy"` images — re-verified each URL returned `200 OK` directly via `curl` and confirmed this was a lazy-load timing artifact in my own probe, not a real defect; after scrolling the full page to trigger lazy-load, all 22 images report `complete && naturalWidth > 0` cleanly at every width.

## Pass 3 summary for design-lead / main-lead

**PASS.** All 5 scoped re-check items hold:
1. Diff scope genuinely limited to the cost row, draft flag, and proposal — hero, Trash, page A, sections, and motion untouched.
2. Rendered cost row is byte-identical to source COPY-B at `3088502`.
3. Word count 550, confirmed via the canonical counter script, not a manual approximation.
4. Acceptance: 148/0 Chromium, 144/0 WebKit, zero hidden FAILs.
5. Proposal page: no overflow, no broken images at 320/390/1440/1920 (after correcting my own initial lazy-load false-positive).

No findings. No `landing/` files touched. No fixes applied by this seat. Recommend proceeding with slice 03 build on this SHA.
