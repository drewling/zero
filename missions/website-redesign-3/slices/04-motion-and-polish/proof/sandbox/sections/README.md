# Selected page B section-motion sandbox

Prototype only, authorized by main-lead at 00:58Z and design-lead at 01:02Z on 2026-09-30. Contract: `MOTION-SPEC.md` §4.2 at `e58ff8f`. Frozen markup, styles, assets and reference stories: `39aa729`.

This is not a landing implementation, final copy, owner approval, independent QA or slice completion. `landing/` remains untouched. The copied page's hero is deliberately **static context**. The selected animated hero remains the separate [hero B fixture](../hero-b/README.md). Future integration must combine that hero's reserved geometry with the approved page and copy at an exact slice-03 SHA.

## Files and boundaries

- `index.html` is the selected page B snapshot with local asset paths, static hero context and an in-flow sandbox proof label after the footer.
- `kit/` contains the frozen reference CSS and relevant font assets, not a new design system. Future copy and layout changes in the designer's active files do not mutate this fixture.
- `sections.js` supplies four data-driven stories to the shared `../motion.js` runner. Row and line counts come from the actual DOM. Every story restores its complete final state on success, cancellation and error.
- `sections.css` reserves the Copy control's slot, enforces the HTML hidden fallback, and paints Terminal glyphs without altering the complete command's line boxes.
- `reference/` preserves exact before-state runners and designer stories for paired RED checks. They are not production code.
- `test-sections.mjs` serves this fixture on an ephemeral loopback port and uses an installed headless Playwright browser. No dependency was installed or added to the application.

## Reader behavior

The default HTML is complete. No JS, `?static`, reduced motion, or a reduced preference with `?frame=0` leave the truthful final scene. Under normal motion:

1. A scene pre-arms just below the fold and plays once when at least 35% of the scene or viewport is visible.
2. A scene visible at first sight, or reached by a same-page link/hash within 1.2 seconds, stays final and never rewinds.
3. Before-install Get Info draws integer zoom rectangles from the app icon, then reveals the ledger rows.
4. Rules hops Accounts, Undo, Settings, then draws all 13 authored lines in pairs.
5. Undo reveals five full rows plus the empty, aria-hidden cut sixth row, then the restore balloon points to row five.
6. Terminal reveals two command glyphs per step. The immutable full command reserves its wrapping and remains the source for Copy. After playback, its cursor blinks three times using `steps(1)`, then rests.

These stories create no cursor DOM. Decorative zoom and typing sprites are aria-hidden and cannot intercept input. Reduced-motion changes, viewport changes, errors and visibility interruptions remove sprites and restore complete content, without later asynchronous mutations.

`?frame=0`, `1`, `2` expose section stills. The Terminal has two frames, so its last QA frame is its **complete final command**, not an intermediate typing sample. The partial-typing PNGs in `evidence/*-term-live-partial.png` come from actual reader scrolling.

## Copy

The Copy button ships hidden. It is only shown when a secure context has a callable Clipboard API. No JS or no API leaves the full selectable command and no dead button.

Keyboard activation preserves button focus. Success announces `Copied` through a visible polite status. Rejection selects the full command, cancels active typing before selection, and announces `Copy manually: press Command-C.`. Concurrent pending writes are ignored. Nothing runs the installer command.

## Run

From the repository root:

```sh
CAPTURE=1 node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/test-sections.mjs
ENGINE=webkit WEBKIT_EXECUTABLE="$HOME/Library/Caches/ms-playwright/webkit-2336/pw_run.sh" node --test missions/website-redesign-3/slices/04-motion-and-polish/proof/sandbox/sections/test-sections.mjs
```

WebKit 2336 is a compatible installed alternate, not the package's pinned revision and not Safari acceptance. WebKit 2248 failed before page execution because its protocol lacked `Console.enable`; its failed log is retained. See [verification and requirement mapping](evidence/VERIFICATION.md) for exact observed results, source hashes and remaining boundaries.

## Next authorized boundary

Designer visual judgment and final-copy selection remain external. Gate B, a real slice-04 assignment and the approved slice-03 SHA are required before integration. Production build, deployment, Lighthouse and Safari verification have not been performed. Do not port this provisional page or declare the landing complete from these fixture results.
