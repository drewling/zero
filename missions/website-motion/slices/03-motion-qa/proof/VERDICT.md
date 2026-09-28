# Independent motion QA verdict — OPR.99.0.2.3

**Candidate SHA:** `0505816f97aa56e7cde4c821100a2b40bf116e86`
**Baseline SHA (prior independently-QA'd candidate, pre-motion):** `57deff2`
**QA method:** Playwright real-engine automation (Chromium + WebKit) at true viewport widths (1440/390/320), local static server (`python3 -m http.server` from `landing/`, since the Docker daemon is unavailable in this environment — same constraint noted in slice 02's own PROOF.md). Explicitly not device emulation; framed as a real-browser substitute per standing instruction.
**Full raw log:** `proof/command-output.txt`. Screenshots: `proof/*.png`.

## Requirement-by-requirement verdict

### 1. Visual motion states at 1440/390/320 vs storyboard, no overflow/layout shift — **PASS**

- Desktop 1440 sort-track states (t=0/700/1300/settled) and rail states (t=0/450/900) captured and structurally compared against `storyboard/d-sort-*.jpg` and `storyboard/d-rail-*.jpg`: same staggered-ticket, trail, bloom, and archive-tag-flight visual language. Minor per-frame timing differences vs the storyboard stills are expected (different capture method, not a defect) — same overall choreography.
- **True narrow-viewport captures (390×844, 320×700)** for sort-mid, sort-settled, install-boarding, and reduced-motion states. This directly closes the brief's own named gap: the storyboard's mobile frames came from a 390-wide *iframe inside desktop Chrome*, not a true viewport, and two mobile states (install, reduced-motion) were never captured at all because the prototype's screenshot tooling repeatedly timed out. This QA used Playwright's real viewport sizing to capture all of them.
- **No horizontal overflow** at any tested width/state: `scrollWidth === clientWidth` confirmed at 1440, 700 (mid-resize), 390, and 320 in every motion state tested, including full-page.
- **Verdict-word scramble regression check** (the brief's own named historical bug — an earlier prototype pass showed the wrong word mid-flight and had to be pulled): sampled the live DOM every 50ms across the *entire* animation duration (49 samples) at both 1440 and 320px. Zero mismatches — the verdict word is always the correct real word, never scrambled, at every width tested.
- Resize across the 760px breakpoint mid-session (1440→700 live) redraws the canvas geometry correctly via `ResizeObserver` with no overflow and no state loss (`sorted` class persists correctly).

### 2. Keyboard/touch/FAQ/interrupt/hidden-tab/resize behavior — **PASS**

- **Keyboard tab order**: diffed candidate vs baseline (57deff2) across the full page (40-tab walk). Identical except two new stops (`sort-replay`, `rail-replay`) inserted exactly where they sit visually — no existing tab stop reordered, added, or broken.
- **Focus-within reveal**: install-steps content reveals instantly on keyboard focus (computed style confirms `transition-duration: 0s`, not just a fast visual illusion), including the safety-critical "Read this first" installer warning.
- Both replay buttons are keyboard-focusable and Enter-operable, producing the same effect as a mouse click.
- **Touch**: tap on both replay buttons at 390px (touch-enabled context) works correctly.
- **FAQ**: opens/closes correctly with the new `.faq-ready` motion attached; no regression.
- **Interrupt/re-entry**: mid-run replay click restarts from 0 immediately (no queueing); 5 rapid-fire clicks do not stack or explode rAF usage (bounded to one active timeline via `cancelAnimationFrame`). Rail flip mid-move updates the button label immediately and settles to one consistent state after rapid double-flipping.
- **Hidden-tab pause/resume**: simulated `document.hidden` via `visibilitychange` — 0 rAF calls scheduled during an 800ms hidden window (`timeline.pause()` works), rAF resumes immediately on visibility return, and the animation completes correctly to the right final state after the full cycle. No desync.
- **Idle-frame-budget**: 0 rAF calls scheduled in a 1-second idle window after the animation settles — confirms no leaked animation loop.

### 3. Reduced-motion/no-JS/no-Canvas fallback, focus/contrast/a11y — **PASS**

- `prefers-reduced-motion: reduce`: sort track and replay button stay hidden, rail diagram renders instantly at its final settled state (no animation), verdict words are the original untouched plain text (no `.status-word` wrapper spans even created), `motion-reduced` class applied. Confirmed via **true Playwright `reducedMotion: 'reduce'` context emulation**, not a manual CSS media-query proxy.
- No-JS (`javaScriptEnabled: false`): canvases/replay/rail all hidden via the server-rendered HTML `hidden` attribute — this is *not* a JS-toggled fallback, it degrades correctly even with zero script execution. Verdicts remain plain correct text. Copy button (which needs the Clipboard API) is the only element that correctly stays hidden; the install command text itself remains fully visible.
- No-Canvas-context (`canvas.getContext` forced to return `null`): sort/rail gracefully hide, **zero page errors** on load or reload, static content fully intact. Visually matches the brief's own `d-nocanvas-sort.jpg`/`d-nocanvas-undo.jpg` reference frames.
- **Accessibility tree check** (CDP `Accessibility.getFullAXTree`, not just DOM inspection): confirmed the install-steps' pre-reveal visual clip trick (`opacity:.001; clip-path: inset(...)`) is *purely decorative* — every piece of content, including the "zero isn't notarized by Apple" safety warning, is exposed to assistive tech (`ignored: false`) at all times, never actually hidden from screen readers.
- **Canvas `aria-hidden`**: both canvases confirmed `aria-hidden="true"` in the live DOM.
- **Verdict-word legibility**: see the exhaustive 50ms-interval scramble check above — this is the brief's own named "historically critical" risk and it does not reproduce anywhere in this candidate.
- **Contrast** (live-measured WCAG relative luminance from rendered computed styles, not from spec claims): `.sort-replay` 15.89:1, `.rail-replay` 10.41:1, dimmed pending-verdict-word state 8.67:1 — all comfortably AAA (≥7:1).
- **Focus rings**: both new buttons show a clearly visible 3px solid outline on `:focus-visible`.

### 4. Performance vs baseline, node tests, Docker build/smoke, installer/routes — **PASS, with one blocked item (not waived)**

- **Node tests**: `node --test` re-run fresh against the candidate — 5/5 passing.
- **Source checks**: `site.js` syntax valid, no prototype-only debug hooks shipped (`?seek`, `?rm`, `?nocanvas`, `?slow`, `?at=`, `stats()`, `bench()`, `mobile.html`, `window.zeroMotion` — zero matches via grep). The internal `seek()` method exists only as a private closure API used for legitimate reduced-motion instant-settle logic, never exposed globally.
- **Scope discipline**: `git diff --stat` between baseline and candidate touches exactly `landing/index.html` (+6 lines, markup only), `landing/site.css`, `landing/site.js`, `landing/test-site.mjs` — matches the brief's stated scope ("DOM, CSS and JS only... no new assets or dependencies") exactly. `nginx.conf` and `Dockerfile` are byte-identical to the baseline. No existing visitor-facing copy changed (confirmed via line-level diff of `index.html`: only new canvas/button/rail-wrap markup was added).
- **Byte budget**: measured actual gzip delta directly (not trusted from the brief's prototype-stage estimate) — **+4,100 bytes gzip total** (JS +3,246B, CSS +854B) against a ≤10KB budget. Notably leaner than the prototype's own ~7.4KB estimate, confirming prototype-only instrumentation was correctly stripped before shipping.
- **Performance / frame budget** — this was the brief's other explicitly-named "not proven" gate (the prototype's live rAF timing was measured only through a throttled automation browser and flagged as inconclusive on the max). Re-measured **per-rAF-callback script execution time** (the actual metric named in the brief's budget row, not frame-to-frame interval) using `performance.now()` wrapped around each callback:
  - Sort track, unthrottled: mean 0.23ms, max 1.6ms
  - Sort track, 4× CPU throttled (CDP `Emulation.setCPUThrottlingRate`): mean 0.80ms, max 4.8ms
  - Rail diagram, unthrottled: mean 0.20ms, max 0.3ms
  - Budget was mean ≤4ms / max ≤16ms — passed with wide margin in every case, including under throttling.
- **Cross-browser**: full-page scroll-through error sweep on Chromium and WebKit (the Safari engine, directly relevant since this is a macOS-only product) — **zero page errors, zero console errors** on either engine. `:has()` CSS selector (used for the sorted-row styling) confirmed supported in WebKit. Firefox was not installed locally and not exercised; noted as a minor, non-blocking coverage gap since Firefox is not a target platform for this product.
- **Routes**: `/`, `/site.js`, `/site.css`, `/privacy.html`, `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/og.png` all 200 on the local static server. `install.sh` syntax valid (`bash -n`).
- **Docker build/smoke — BLOCKED, not waived.** The Docker daemon is unavailable in this environment, exactly as noted in slice 02's own `PROOF.md` and flagged by main-lead's QA-gate reminder. This QA compensated with everything checkable without a running container: source syntax, `nginx.conf`/`Dockerfile` diff-against-the-already-QA'd baseline (byte-identical, confirming infra was untouched), and all static-file routes reachable via the fallback server. The one thing this QA genuinely cannot verify locally is the live nginx `/install.sh` rewrite route and a true containerized boot. Per main-lead's note, Docker smoke may run as an isolated production-server preflight after this source-level QA passes, with no deploy until that resolves.

### 5. Mission-level guardrails (self-validation addendum) — **PASS**

Re-checked directly against `mission.yaml`'s explicit boundaries and the approved-direction constraints in `NOTES.md` (2026-09-28 20:26Z: "no pointer-reactive effect"):

- **No pointer-reactive effect**: grep for `mousemove`/`pointermove`/`mouseenter`/`pointerenter` listeners in `site.js` — zero matches. The Canvas effects respond only to scroll-into-view and explicit button clicks, never cursor position.
- **No autoplay sound**: zero `<audio>` elements, zero `AudioContext`/`.play()` usage anywhere in the shipped JS.
- **No scroll-jacking**: zero `preventDefault` calls on wheel/scroll listeners; native scroll behavior is fully preserved.
- **No fake inbox activity**: the sort/rail canvases only animate the same static example rows already present in the approved copy — no synthetic new-message arrival or live-looking activity was added.
- **Pre-existing hero flap-board animation** (the departure-board-style headline tiles, explicitly called out in mission NOTES.md as needing to remain settle-under-1s and reduced-motion-suppressed): `site.css` diff against baseline `57deff2` for this rule block is byte-identical — confirmed via direct diff, not inference, that this mission did not touch or regress it.

## Overall verdict: **PASS, with one named residue**

All storyboard-scoped motion, accessibility, interaction, fallback, and performance requirements in SPEC.md items 1-3 and the testable parts of item 4 are met, with direct evidence (not inference) for every claim, including live re-measurement of both gates the brief itself flagged as unproven (mobile narrow-viewport visual states, and rAF performance under throttling). Both are now closed with passing evidence.

**Residue:** Docker build/smoke could not be run locally (daemon unavailable). This is an environment constraint shared with slice 02's own QA, not a defect found in the candidate. Recommend running Docker smoke as an isolated preflight (per main-lead's guidance) before deploy, specifically to confirm the nginx `/install.sh` rewrite route, which the local fallback server does not replicate.
