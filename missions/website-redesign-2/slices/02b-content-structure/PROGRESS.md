# Slice 02b progress

- 04:37Z: Claimed `qitem-20260929043654-3d8257bd` (owner: design-lead@zero). Read SPEC, mission NOTES, the kernel method note, PRODUCT.md and live B `landing/index.html` (901 words).
- 04:38-04:50Z: Checked product truth against the source and the shipped v1.7.0 DMG. Found that Settings → Daily routine never installs a schedule (only `bin/zero schedule` does). Confirmed the signals `last_from_owner` (deterministic archive) and `replied_before` (a Jev input), the starred exclusion, keep-on-failure, the Jev inputs (sender, subject, a snippet of at most 160 characters, the policy), draft providers, and the installer's gates and dependencies.
- 04:51Z: Wrote the comp `proof/comp/index.html` on B's stylesheet. 600 words.
- 04:54Z: Wrote `proof/CONTENT-PROPOSAL.md`: critique, before/after outline, full copy, fact trace, corrections and cuts, owner questions, limits.
- 04:56Z: Aside captures viewed (5 desktop sections, 3 phone frames, past right edge 0).
- Status: **awaiting owner approval** of the outline and copy, plus Q1-Q3. Slice 02c stays gated.
- 04:59Z: Self-audit corrections after the handoff.
  - "Starred mail: Never touched" is now "Runs never archive it". The code only stops runs from archiving starred mail, and you can still archive a starred thread yourself.
  - The Jev data-flow row now includes "what it has learned from you". `_jev_state` also sends `learned_preferences`, so the earlier wording under-disclosed.
  - The word count is now 608 (was 600) and still within the 500-650 target.
  - This was a text-only change inside existing paragraphs.
- 05:02Z: Acceptance-path checks (evidence in PROOF.md, "Acceptance-path checks").
  - Retook `d4-undo.jpg` and `d5-before.jpg` with Aside. Both show the ed152a5 wording.
  - The TypeSafe keys link opens a real "API keys" page in the owner's authenticated browser (Aside). The 403 was curl only.
  - The live install path works end to end: `zero.headless.com/install` redirects (302) to raw `macapp/install-zero.sh`, and the SHA-256 of the fetched file equals the repo file (e3e29530...). `/install.sh` redirects (302) to the GitHub view, and `/privacy.html` and `/terms.html` return 200.
  - GitHub repo and Releases return 200. All 6 in-page anchors resolve.
  - Parity between §3 and the comp: 62 lines checked, and 54 match the comp word for word. The other 8 are layout notes and markup, not copy: the menu, button pair, caption, window label, command and footer, plus the notarized note and meta description, which only failed because of italic markers. I checked those last two by hand and they match.
