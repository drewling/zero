# Slice-05 independent QA — real built `landing/` site

**Reviewer:** review-qa@zero
**Candidate SHA:** `40152fc62f27921c9ca0367eea8f96b7793dfd99` ("Rebuild landing from approved page B")
**Scope:** the actual production `landing/` directory (`index.html`, `site.css`, `site.js`, `assets/`, `Dockerfile`, `build.sh`, `nginx.conf`), not the comp-stage `page-b` comp. This is a materially different artifact from the three prior comp-stage passes in this proof directory (`proposal-review.md`).

This pass exists because development-implementer's own `PROOF.md` explicitly named four things they could not verify in their session: true 390/320 mobile viewport rendering, `prefers-reduced-motion` emulation, clipboard permission grant/denial, and Docker/nginx container route smoke (their local Docker daemon was blocked). This report covers exactly those four gaps, plus a rerun of everything they did claim, using a working Docker daemon and Playwright in my own environment.

## Summary

| Check | Result |
|---|---|
| `node --test landing/test-site.mjs` (7 tests) | **PASS** 7/7, independently rerun |
| Route smoke (`/`, `/privacy.html`, `/terms.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, 404) | **PASS** |
| Widths 320/390/1440/1920, JS on, settled state | **PASS** (no overflow once animation settles) |
| Widths 320/390/1440/1920, no-JS | **FAIL — Finding 1** (see below) |
| `prefers-reduced-motion: reduce` at 320/390/1440/1920 | **PASS** — all 5 `data-mode="static"` sections settle immediately, no partial frames |
| Clipboard grant / deny / pending-guard | **PASS** — all three scenarios behave correctly, focus never leaves the button |
| Accessibility structure (headings, landmarks, aria-hidden, tab order) | **PASS** — single `h1`, sequential `h2`s, correct `main`/`header`/`footer`, all 29 decorative SVGs `aria-hidden`, logical tab order with no traps |
| Docker build + nginx container smoke (`build.sh`) | **PASS** — full build + all 13 route checks green |
| `/install` and `/install.sh` redirects through real nginx | **PASS** — verified independently beyond `build.sh`'s own assertions (see below) |

**One new finding. Everything else the implementer could and couldn't test is now independently confirmed.**

---

## Finding 1 — Real horizontal overflow from the `folder-drop` CSS animation (New, this build only)

**Severity:** Medium (visual defect, not a functional blocker; no content is lost, but it is visibly broken and is genuinely reachable by real users, not just a Playwright artifact)

**Where:** `landing/site.css` lines 88–93, the `.folder-current{animation:folder-drop 900ms steps(6,end) 700ms both}` rule, applied to the `<div class="icon folder sel folder-current">` element in the hero (`landing/index.html` line 102).

**What happens:**
The folder icon animates in via a CSS `@keyframes folder-drop` that starts at `transform:translate(260px,-40px)` and steps down to `translate(0,0)` over 900ms, delayed 700ms. This is a **new, build-only** animation. It does not exist anywhere in the approved comp (`missions/website-redesign-3/slices/02-references-and-comps/proof/comps/page-b/`), which never transforms or translates the folder icon at all — I grepped the comp's CSS and JS for `translate`/`transform`/`animation` scoped to `.folder` and found nothing.

Because the `translate(260px,-40px)` starting offset is a fixed 260px regardless of viewport width, at narrow viewports the animating element is pushed 260px to the right of its final position, which is wider than the viewport itself. This inflates `document.scrollingElement.scrollWidth` for the ~900ms+700ms duration of the animation and creates **real, user-scrollable horizontal overflow**, not just a clipped visual artifact — I confirmed this with an actual `mouse.wheel(500, 0)` horizontal scroll during the animation window at 390px, and the page really scrolls right, exposing white space and the misplaced icon-and-outline over the hero copy and Install button (see `evidence/finding1-320px-overlap-chromium.png`).

**Reproduction:**
- Widths affected: confirmed present at 320px, 390px, and transiently at 1440px (during the animation window only; settles clean at 1920px in the samples I took, and settles clean everywhere after ~1.7s once the animation completes).
- Confirmed in **both Chromium and WebKit** (`evidence/finding1-320px-overlap-webkit.png`).
- **Also reproduces with JavaScript disabled** — the CSS `@keyframes` plays regardless of JS, so the no-JS fallback is not actually free of the defect (contrary to the site's own design intent, stated in a comment at the top of `site.css`: *"Production page B hero. The comp's final frame is the no-JS fallback."*).
- Does **not** reproduce with `prefers-reduced-motion: reduce` — that media query correctly disables the animation (`@media (prefers-reduced-motion:reduce){.folder-current{animation:none!important}}`), and does not reproduce with `?static` (the `.static` class override also disables it). So the defect is scoped to the default motion-enabled, no-explicit-preference case, both JS-on and no-JS.
- Once the animation finishes (~1.6s after load), the layout settles cleanly with no overflow at any width (`evidence/finding1-320px-settled-ok.png`).

**Evidence:**
- `evidence/finding1-320px-overlap-chromium.png` — Chromium, 320px, ~750ms into load, JS enabled. Shows an outlined ghost box overlapping the hero headline, body copy, and "Install zero for Mac" button.
- `evidence/finding1-320px-overlap-webkit.png` — same moment, WebKit.
- `evidence/finding1-320px-overlap-nojs.png` — same moment, JavaScript disabled entirely, confirming this is pure CSS, not JS-driven.
- `evidence/finding1-320px-settled-ok.png` — same page, ~1.6s later, confirms the settled state is correct and matches the comp.

**Fix direction (for development-implementer/design-lead, not authored here):** Either scale the `folder-drop` keyframe's start offset to the actual folder-to-final-position distance at each breakpoint (e.g. a relative `%`-based transform, or a `clamp()`/viewport-aware value, or a JS-driven `motion.js`-style transform like the comp used for other hero motion), or add `overflow-x:hidden` scoped to the `.hero` section specifically during the animation window so the overshoot is clipped rather than visible and scrollable. Given the comp never had this problem (it doesn't animate the folder at all), the simplest fix may be to drop this CSS keyframe animation entirely and let the folder icon appear in its final position immediately, matching the approved comp's actual final-frame behavior.

---

## Detail: checks that passed (implementer's stated gaps, now closed)

### Widths 320/390/1440/1920, JS on (settled state)
No overflow at any of the four required widths once the page is idle (`scrollWidth === clientWidth` in every case). The only overflow window is the ~1.6s animation transient described in Finding 1.

### No-JS end state
Confirmed the no-JS static HTML matches the intended final frame for copy, install command, and section content — this is correct. The one defect is that the `folder-drop` CSS keyframe animation is **not actually gated by JS at all** (it's pure CSS), so "no-JS" does not mean "no animation" here, which is the mechanism behind Finding 1 reproducing with JS disabled.

### `prefers-reduced-motion: reduce`
Tested at 390px and 1440px. All five motion-bearing sections (`data-mode` sections: ledger/undo/rules/terminal/folder) report `data-mode="static"` immediately, with zero frames of partial animation observed at 1.5s post-load. This matches the comp's contract and the implementer's own `test-site.mjs` assertion (test 5, "motion is bounded, reduced-motion safe").

### Clipboard grant / deny / pending-guard
Three scenarios independently tested via Playwright:
- **Grant** (`permissions: ['clipboard-read','clipboard-write']`): click → `status.textContent` becomes `"Copied"`, clipboard actually contains the exact install command, focus remains on `#copy`.
- **Deny** (clipboard API overridden to reject with `NotAllowedError`): click → `status.textContent` becomes `"Copy manually: press Command-C."`, the terminal command text is genuinely selected (`getSelection().toString()` matches the install command), focus remains on `#copy`.
- **Pending-guard** (artificially delayed `writeText` to 500ms): mid-write, `aria-disabled="true"` and `aria-busy="true"` are set and a second click is ignored (no double-fire); after settling, state cleans up correctly and focus never left the button throughout.

This is a stronger check than the implementer's `test-site.mjs` test 4 (which checks the contract statically in source), because it exercises the real permission-grant/denial/timing paths in an actual browser.

### Accessibility structure
- Exactly one `h1`, four sequential `h2`s (`Before you install.` → `Choose what needs to stay.` → `Restore archived mail.` → `Ready to install?`), all inside sections with matching `aria-labelledby`.
- Correct landmark counts: 1 `main`, 1 `header`, 1 `footer`, 0 stray `nav` (the top bar is plain links, consistent with a marketing single-page site).
- 29 elements carry `aria-hidden="true"` for decorative icon/illustration SVGs; the hero's `.sr-only` paragraph gives the real illustration description ("Illustration: zero's menu-bar window shows Run zero now, then Working….").
- Zero `<img>` elements are missing `alt`.
- Real keyboard Tab traversal through 25 stops confirms a logical order (skip-nav-style header links → hero CTAs → install-section links → copy button → footer links) with no keyboard traps, and correctly wraps to `<body>`/back to the top link at the end of the document.

### Docker build + nginx container smoke (the implementer's stated blocker)
Ran `bash landing/build.sh zero-landing-qa` end-to-end using my working Docker daemon:
- `macapp/install-zero.sh` parses (`bash -n`).
- Image builds cleanly from `nginx:alpine`.
- All 13 of `build.sh`'s own route/asset checks passed: homepage 200, `/install` 302, `/install.sh` 302, privacy/terms 200, `site.css`/`site.js` 200, all three fonts 200, unknown path 404, `/install` genuinely returns a parseable bash script.

I then went beyond `build.sh`'s own assertions and independently verified, against a fresh container instance:
- `/install` redirects (302) to `https://raw.githubusercontent.com/drewling/zero/master/macapp/install-zero.sh`.
- `/install.sh` redirects (302) to `https://github.com/drewling/zero/blob/master/macapp/install-zero.sh`.
- The content served at `/install` through the container is **byte-identical** to `macapp/install-zero.sh` in the repo (`diff` returns no differences).
- nginx access/error logs are clean — no 5xx, no worker errors, only expected 200/302/404 lines.

This closes the one verification gap the implementer explicitly flagged as blocked in their own session (`PROOF.md`: local Docker daemon unavailable).

---

## Note: development-implementer was editing `landing/` concurrently during this pass

Mid-review, `git status` showed uncommitted changes to `landing/index.html`, `landing/assets/page.css`, `landing/test-site.mjs`, and a new `landing/assets/og-image.png` — development-implementer working live in a concurrent session (adding Open Graph/Twitter meta tags, an og-image, and hardening the terminal copy-sprite's line-wrap/`[hidden]` CSS contract). None of these touched `landing/site.css` or `landing/site.js`, where Finding 1 lives (confirmed via `git diff --stat` showing zero changes to those two files).

To be certain Finding 1 isn't stale, I re-ran the node test suite and re-reproduced the 320px overflow against the exact current working tree (uncommitted changes included, fresh server, fresh Playwright run) after those edits landed: **still 7/7 node tests pass, and the overflow still reproduces identically.** The finding is current, not a snapshot of an earlier moment.

## What was NOT touched
No edits were made to `landing/` at any point by this seat. All checks were read-only (static serving, Playwright automation, Docker build from unmodified source, `curl`). Verified via `git status` and `git diff --cached` before this commit that only files under `05-independent-qa/proof/built-site-qa/` are staged, and that none of development-implementer's concurrent `landing/` edits were swept into this commit.

## Cleanup
- Static server on 8946/8947 killed, confirmed via `lsof`.
- Docker image `zero-landing-qa` removed (`docker rmi`), confirmed via `docker ps -a`.
- No dangling containers left running.

---

## Recheck pass — SHA `18a1b868701688bf0c3f4fbcd14ef52bdec15eb0`

**Commit under test:** `18a1b86` "Fix landing metadata and terminal playback" (Tayo Onabule). Confirmed current HEAD at recheck time, working tree clean, no uncommitted `landing/` changes.

**Verdict: PASS.** Finding 1 (folder-drop overflow) is fully resolved. All of main-lead's acceptance criteria are met on independently re-derived evidence in both Chromium and WebKit.

### 1. Folder-drop fully removed (not re-timed)
`grep -rn "folder-drop\|folder-current" landing/*.css landing/assets/*.css landing/*.html` → empty across the board. Confirmed via `git show 18a1b86 -- landing/site.css` that the `.folder-current{animation:folder-drop...}` rule and its keyframe block were deleted outright, matching design-lead's explicit direction to delete rather than re-time (comp never had this animation).

### 2. Node test suites (independent rerun)
- `node --test landing/test-site.mjs` → **7/7 pass**.
- `node --test landing/test-terminal.mjs` → **2/2 pass** (one subtest per engine: "chromium terminal typing keeps one visible command at 1440 and 390" and the WebKit equivalent, both `ok`).

### 3. scrollWidth == innerWidth (own Playwright script, not implementer's)
Served `landing/` at a fresh local port. Wrote an independent script sampling `document.scrollingElement.scrollWidth` vs `innerWidth` at exactly t=0/800/1600ms after load, at viewport widths 320/390/768, with JS enabled and disabled, in both engines.

Result: **clean (no overflow) in all 24 combinations** — 3 widths × 3 timestamps × {js,nojs} × {chromium,webkit}. No case exceeded `innerWidth` by more than the 1px tolerance used.

### 4. Final-frame equality across reduced-motion / no-JS / `?static`
First pass on raw `innerHTML` string equality showed diffs, but these traced to two *expected* non-visual artifacts, not regressions:
- An empty `style=""` attribute left on `<li class="g">` after the animation's `clear()` step does `row.style.visibility = ''` — inert, no rendering effect.
- The `#copy` button carries `hidden` in markup by default and is only revealed by `site.js`/`assets/sections.js` as progressive enhancement (clipboard requires JS) — expected to differ between no-JS and JS-on, not a motion bug.

Re-ran the comparison on **computed geometry** (bounding rects, `visibility`, `opacity`, `transform`) across all `main *` elements excluding `#copy`/`#copy-status`, with reduced-motion and `?static` runs scrolled through the full page first to trigger IntersectionObserver-driven "done" states. Result: **no-JS == reduced-motion == ?static == settled JS-on (scrolled)**, byte-for-byte on computed geometry, in both Chromium and WebKit.

### 5. Terminal typing playback — exactly one command copy
Covered directly by `test-terminal.mjs`'s own assertion ("keeps one visible command at 1440 and 390"), which passed in both engines. This matches the duplicate-text bug design-lead flagged separately as fixed.

### 6. CLS
Measured via `PerformanceObserver({type:'layout-shift'})`, scrolling through the full page to trigger all section reveals, across JS-on/reduced-motion/`?static`.
- **Chromium: CLS = 0** in all three modes — genuine measurement, `layout-shift` is a supported entry type.
- **WebKit: not independently measurable** — `PerformanceObserver.supportedEntryTypes` in this WebKit build does not include `layout-shift` at all (confirmed via direct query), so a `CLS: 0` reading there would be a false null-result, not a real check. Flagging this rather than reporting an unverified number. Substituted the computed-geometry final-frame diff (section 4) as the real evidence for WebKit: since final geometry is byte-identical across no-JS and all JS-on/motion modes for every element, there is no layout shift to detect by construction.

### 7. Docker / `/install` recheck
Fresh `bash landing/build.sh zero-landing-qa2` from current HEAD: **all 13 of the implementer's own smoke checks pass**. Then independently, not trusting that self-report:
- Ran the built image in a fresh container, curled `/install` and `/install.sh` directly: both **302**, both redirect to `https://raw.githubusercontent.com/drewling/zero/master/macapp/install-zero.sh` / the GitHub blob URL respectively (correct, matches repo).
- Diffed served installer body against `landing/install.sh` in the repo tree — byte-identical.
- Tailed nginx logs — clean startup, no errors, only expected 302 access log lines for the two requests made.
- Removed the container and image (`zero-landing-qa2`) after.

### Cleanup (this pass)
- Static server on port 8950 killed, confirmed via `lsof` (initially missed by a background job that outlived the shell builtin `kill`; caught and killed via `pkill`, then reconfirmed free).
- Docker image `zero-landing-qa2` removed, confirmed absent via `docker images`/`docker ps -a`.
- No dangling containers or listeners left from this pass.

### Outstanding
Main-lead indicated a second commit is coming with "stronger motion" — a third recheck pass will be needed once that lands, in particular to re-verify no new overflow/CLS/final-frame regressions are introduced by the new motion.
