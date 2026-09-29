# Slice 02c content rebuild proof

Candidate source commit: `1f8e641` (`Rebuild landing copy around visitor decision path`)
Mission: `OPR.99.0.3` / slice `OPR.99.0.3.2c`
Status: build candidate handed to independent QA after proof commit. This is provisional build and QA only. No deploy, push, or release was attempted.

## Delivered

- Replaced the first B candidate's feature-inventory order with the approved six-section visitor path:
  1. Hero and the one job across every connected account
  2. Judgment: “It asks who’s waiting, not who’s writing.”
  3. Ambient use: “Check it with your coffee. Then close it.”
  4. Reversibility: “Nothing is deleted.”
  5. “What it needs, sends and costs”
  6. Install
- Replaced the retired seven-row default-rules table with a two-question Finder-style window explaining the last-message-yours and replied-before signals.
- Removed the FAQ because each answer now has one home in the visitor path.
- Preserved the real `panel-cut.png` app image, compact requirements line, dated folder drop, reduced-motion fallback, legal links, exact install command, and repaired clipboard focus guard.
- Preserved factual disclosures for Apple Silicon/macOS 26, Google sign-in and unverified status, Jev data flow, no zero server receiving email, optional reply drafting, provider billing, and reversibility.
- Kept install semantics at four steps, with the Terminal command and safety warning inside step one.
- Updated `landing/DESIGN.md` and `landing/test-site.mjs` to describe and assert the rebuilt public output.

## Requirement traceability

| Requirement | Concrete check | Observed result |
| --- | --- | --- |
| Approved visitor-first order and wording | `landing/test-site.mjs` heading/order assertions plus real browser DOM inspection | Six headings and order observed: hero, judgment, coffee, undo, needs/sends/costs, install. |
| One job across every account and reversible archive | Node source assertions and rendered hero inspection | Hero contains “Across every account you connect” and “Every archive can be undone.” |
| Judgment differentiator replaces generic filter/table | Node absence assertions and browser inspection | Two-signal window rendered. No `<table>` or old rules-table UI remains. |
| Ambient menu-bar workflow and learning copy | Source assertion and browser heading/content inspection | “Check it with your coffee. Then close it.” and `Run zero now`, `Open loops`, and learning copy are present. |
| Recovery truth | Source assertion and rendered section inspection | Dated label, All Mail/search, Undo/Restore all, starred protection, and uncertain-thread keep behavior are present. |
| Requirements, data flow, replies, and cost | Five fact-row source assertions and local route check | `Your Mac`, `Gmail`, `Your mail`, `Replies`, and `Cost` render in the paper section. Privacy link is present. |
| Install flow | Node assertion counts `<ol class="install-steps">` and requires four `<li>` items | Four items pass. Terminal command and warning are inside step one. |
| Clipboard behavior and focus guard | Existing six Node tests plus real Aside success-path keyboard test | Copy success, denial fallback, pending guard, no duplicate write, and unavailable clipboard pass. Real Enter activation kept focus on Copy and next Tab reached GitHub Releases. |
| Folder-drop motion | Source assertion and real browser computed style/animation inspection | `.folder-current` uses CSS-only `folder-drop 900ms steps(6,end) 700ms both`, settled at final transform/opacity after animation. Reduced-motion rule remains in CSS. |
| No legacy implementation | Node absence test and scoped grep | No table/FAQ, old board selectors, Canvas, rAF, observers, Archivo, or old motion controls in shipped landing source. |
| Public static routes/assets | `curl` checks against local public server | `/`, legal pages, CSS, JS, four fonts, both app images returned 200. `/nope` returned 404. Local Python `/install.sh` returned 404 as expected because it has no nginx redirect. |
| Docker/nginx packaging | `bash landing/build.sh` | Installer syntax passed, then Docker smoke was blocked by unavailable local Docker daemon. `/install` and `/install.sh` redirect behavior remain an unpassed release preflight. |
| True responsive acceptance | Real browser pass at 1440 plus independent QA handoff | 1440x900 measured `scrollWidth/clientWidth = 1440/1440` with no horizontal overflow. The available browser workflow could not set true 390/320 viewports, so QA must own those captures and clipping checks. |

## Checks

- `node --test landing/test-site.mjs` -> 6 passed.
- `node --check landing/site.js` -> passed.
- `bash -n landing/build.sh landing/deploy.sh macapp/install-zero.sh` -> passed.
- `git diff --check -- landing` -> passed before source commit.
- Local static route and asset checks -> homepage, legal pages, CSS, JS, Pixelify 400/600, Geist, Geist Mono, `panel-cut.png`, and `zero-panel.png` returned 200. `/nope` returned 404.
- `grep` absence check -> no retired table/FAQ, board, Canvas, observer, Archivo, or old motion references in landing source. The `facts-table` class is the current five-row facts layout and is not an HTML table.

## Browser evidence and limitations

A real Aside browser pass at 1440x900 inspected the committed source served from `http://127.0.0.1:8877/`. It observed the six-section order, compact requirements line, portrait app image, absent old table and FAQ, four install steps, enabled Copy control, and the dated folder's computed CSS animation. The folder animation settled at its final transform and full opacity.

A second real Aside pass confirmed the 1440 document width remained 1440 with no horizontal overflow, no clipped heading or command, keyboard Copy success retained focus on the button and announced the copied status, and the install DOM contained all four steps. The browser workflow could not resize to true 390x844 or 320x700 or enable reduced-motion emulation, so those checks are explicitly delegated to independent QA rather than substituted with iframe or synthetic emulation.

`bash landing/build.sh` produced:

```text
ok  installer parses
ERROR: Cannot connect to the Docker daemon at unix:///Users/light/.docker/run/docker.sock. Is the docker daemon running?
```

Release preflight must run the Docker image and verify nginx `/install` and `/install.sh` return 302 before deployment. No deployment was attempted.
