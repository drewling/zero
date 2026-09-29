# Slice 02b proof: content and structure direction

**Status: draft ready for owner approval.** Proof only. `landing/` is unchanged, and there was no builder dispatch, QA or deploy.

| Proof-contract item | Where | Evidence |
|---|---|---|
| Source references for load-bearing claims | `proof/CONTENT-PROPOSAL.md` §4 (fact trace) and §5 | Every claim is checked against HEAD `6067190` source (`lib/review_open_loops.py`, `lib/inbox_zero.py`, `lib/keeper_server.py`, `lib/llm.py`, `lib/jev.py`, `macapp/Sources/*.swift`, `macapp/install-zero.sh`, `landing/nginx.conf`, `privacy.html`, `LICENSE`) and against the shipped v1.7.0 DMG from `releases/latest`, mounted read-only 04:41Z |
| Shipped vs aspirational | CONTENT-PROPOSAL §5 "Not advertised" | `npx zero init`, a guaranteed morning run, user-visible probabilities, Apple Mail integration and categories are all excluded, with reasons |
| Word counts | CONTENT-PROPOSAL §2, §7 | The same visible-text script on both pages: live B `landing/index.html` 901, comp `proof/comp/index.html` 608 |
| Before/after outline | CONTENT-PROPOSAL §2 | 7 old sections to 6. Each new section is tied to the visitor question it answers. The FAQ is cut |
| Full proposed copy | CONTENT-PROPOSAL §3 and `proof/comp/index.html` | The same text in both. The comp is the rendered form |
| Each safety/requirement fact in one best place | CONTENT-PROPOSAL §4 | 23 facts traced. "Nothing is deleted" 4 to 1, Jev data flow 2 to 1, drafts-send-nothing 3 to 1, cost 3 to 1. Two deliberate doubles are named with reasons: the requirements gate and the "read the installer" link |
| Required disclosures present | comp | install and legal paths, default-rules caution ("It will sometimes be wrong"), macOS 26 / Apple Silicon, not-notarized warning and dependencies, third-party text handling (Jev, agent CLI), optional reply/send, billing, AGPL |
| Corrections to prototype copy | CONTENT-PROPOSAL §5 | The main one: the old step 4 promised Settings → Daily routine, but in v1.7.0 that setting only rewrites an existing LaunchAgent, and only `bin/zero schedule` creates one. The draft doesn't promise an automatic run (owner Q1) |
| Unresolved product facts | CONTENT-PROPOSAL §6 | Q1 daily run (copy vs app fix), Q2 headline, Q3 section-3 register |
| Viewable comp on approved B | `proof/comp/index.html` (+ `phones.html`) | Uses `landing/site.css`/`site.js`/`assets` via symlinks. All 8 assets returned 200 from `127.0.0.1:8935` |
| Rendered check | `proof/shots/d2-decides … d6-install.jpg`, `phones.jpg` | Aside, 04:56Z: desktop 1440 (innerWidth 1440, scrollWidth 1440), 5 section shots; 390 iframe harness, 3 frames, each `scrollWidth 390 · past right edge 0`. All viewed. An Aside full-page capture repeated the hero (a stitching artifact), so it was discarded and not committed. No hero desktop shot is committed separately, but the hero is the first phone frame, and the desktop hero was viewed in the discarded capture |

**Acceptance-path checks (05:02Z):**
- The TypeSafe keys link opens a real "API keys" page in the owner's authenticated browser, checked with Aside. The earlier 403 was curl only.
- The live install command `curl -fsSL https://zero.headless.com/install` redirects (302) to raw `macapp/install-zero.sh`. The fetched file's SHA-256 equals the repo file.
- `/install.sh` (the "Read the installer first" link) redirects (302) to the GitHub source view. `/privacy.html` and `/terms.html` return 200 live.
- GitHub repo and Releases return 200. All 6 in-page anchors resolve.
- Copy parity between §3 and the comp: 54 of 62 lines match word for word. The other 8 are layout notes, and I checked two of them by hand.
- `shots/d4-undo.jpg` and `d5-before.jpg` were retaken after ed152a5 and viewed.

**Not verified:**
- True device emulation. The phone view is a 390 iframe.
- Whether the owner prefers this story. That is the gate, and it belongs to the owner through main-lead.
