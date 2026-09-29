# Truth trace: zero copy v3

Checked 2026-09-29 UTC by design-copywriter@zero. Product/code baseline: `bc9f296` (only proof artifacts are changing). Locations below refer to `proof/COPY.md` sections by heading and exact phrase, so implementation can preserve the truth without relying on authoring-line numbers. Source line ranges are repository-relative. This is a read-only audit, not a live inbox run or a new app release.

## Claim and disclosure map

| Claim/disclosure | New location and wording | Source file:line and check |
|---|---|---|
| Mac app, Gmail inbox management, no new mail client | Hero: “Clean up your Gmail inbox on your Mac.” Subhead: “Keep using Gmail or Apple Mail.” | `PRODUCT.md:9–15,31–34,74`; `macapp/Sources/PanelView.swift:490–492` shows kept-mail count and Gmail destination. `macapp/build.sh:22` compiles the Mac binary. |
| Keep action mail, archive the rest | Hero and decision section: “keeps the emails you need to deal with”; “It keeps replies you owe, direct requests, payment problems, legal matters and deadlines with consequences.” | `keep-policy.md:8–23`; `lib/review_open_loops.py:974–998,1070–1099,1746–1758`. The model makes mistakes, which the next paragraph explicitly says. This is the intended policy, not a guaranteed classification accuracy claim. |
| Read/check threads with an AI model, configurable rules | Decisions: “An AI model checks each thread against your rules.” “Settings → Rules.” | `lib/review_open_loops.py:974–998` builds structured per-thread state with policy; `macapp/Sources/PanelView.swift:1320–1322` exposes Rules. We do not claim the model receives full bodies. |
| Familiar keep/archive examples | Demo sentences and 12 fictional rows | `keep-policy.md:10–23`; `lib/review_open_loops.py:1160–1164,1754–1758` handles last-message-from-owner. Editorial examples, clearly captioned, not a measured outcome or actual customer mail. We rejected a sign-in alert as an archive example because alerts can require action. |
| Manual run is shipped, multiple connected Gmail accounts | Demo: “Click Run zero now on your Mac to sort the Gmail accounts you connect.” Install repeats the real control | `macapp/Sources/PanelView.swift:2941–2947`; `lib/keeper_server.py:294–310,392–412`; `macapp/Sources/PanelView.swift:492` and `PRODUCT.md:115–118` establish accounts and Gmail. No unattended schedule promised. |
| Opening kept mail in Gmail | Demo: “Open a kept email in Gmail…” Hero illustration's supporting line | `macapp/Sources/PanelView.swift:490–492` explicitly says tap to open in Gmail. The app also has an in-panel preview, but this page is not selling a new email client. |
| Reversible archive, no mail deleted | Hero: “Undo any archive.” Recovery: “Undo an archive. Nothing is deleted.” | `PRODUCT.md:25–29`; `lib/review_open_loops.py:1785–1793` adds recovery label and removes only INBOX. No mail-delete request in this archive path. |
| All Mail, searchable, dated label | Recovery paragraph: “Archived mail stays searchable in Gmail's All Mail, with a dated recovery label.” | `lib/inbox_zero.py:5–6,225–238`; `lib/review_open_loops.py:1789–1793`; `macapp/Sources/PanelView.swift:2774,2851`. Archive removes the INBOX label, not the message. |
| Restore one or a day's archives | Recovery: “Undo tab…restore one email…Restore all for a day's archives.” | `macapp/Sources/PanelView.swift:1017–1027,1053–1083,1100–1107,1151–1170`; `lib/keeper_server.py:535–599,647–697` implements bulk/individual restore and return to INBOX. |
| Starred mail untouched by sorting | Recovery: “Sorting leaves starred mail alone.” | `lib/review_open_loops.py:152–155` excludes `is:starred` from sorting query. Wording is scoped to sorting, not an assertion that a user can never manually archive starred mail. |
| Uncertain decisions kept | Recovery: “If the model can't decide, the email stays in your inbox.” | `lib/review_open_loops.py:1070–1099` is keep-biased on missing/malformed/uncertain answers, and only archives a corroborated result. It is not a claim that every error is detected. |
| Apple Silicon, macOS 26+, Gmail only | Hero CTA support line | `macapp/install-zero.sh:61–79`; `macapp/build.sh:22`; `lib/keeper_server.py:28–39` Gmail scopes. Installed app is Mach-O arm64, `LSMinimumSystemVersion=26.0`. Apple Mail is a client for the connected Gmail account, not support for arbitrary providers. |
| Google browser sign-in, no password seen | Gmail access field: “Sign in with Google in your browser. zero never sees your password.” | `macapp/Sources/OnboardingView.swift:120`; `lib/keeper_server.py:1502–1506,1542–1558` launches Google OAuth through gws. |
| Google's unverified-app warning | Gmail access field: warning because review has not completed | `macapp/Sources/OnboardingView.swift:104–107`. Preserved plainly, without the app's “safe” reassurance or a blanket endorsement of bypassing a warning. |
| Local app, no zero email-receiving service | Email data field: “zero runs on your Mac”; “No zero server receives your email.” | `macapp/Sources/main.swift:100–110` runs bundled payload locally; `lib/keeper_server.py:5,2646–2652` binds local service; `lib/jev.py:8,33` is direct external TypeSafe API. Distinguishes the project's lack of a hosted receiver from the fact that configured AI providers receive data. Does not say “all data stays on device.” |
| Sorting data sent to TypeSafe Jev | Email data field: sender, subject, short preview, reply-history signals, rules, learned preferences | `lib/review_open_loops.py:974–998` lists precisely those fields, with learned data conditional; `lib/review_open_loops.py:640,691` limits snippets to 160 characters; `lib/jev.py:33` external endpoint. Names Jev only here and in setup/cost, not as the category explanation. |
| Optional drafts through a coding tool | Optional reply drafts: “Claude Code, or another AI coding tool you already use…” | `lib/llm.py:2–12,22–55,76–87` separates classification from prose and dispatches selected installed providers; `macapp/Sources/PanelView.swift:1711` explains drafting provider choices. This wording does not promise compatibility with every possible tool. |
| Draft data sent to selected provider | Optional reply drafts: thread previews, sent-mail samples, writing preferences, saved profile context | `lib/keeper_server.py:1288–1307,1314–1349,1358–1373,1381–1400` assembles the actual prompt and sends it via llm. Draft-guidance text is included in writing preferences. This replaces the old page's narrower thread-preview-only description. |
| No automatic reply send, review first | Optional reply drafts: “Review before clicking Send reply. Nothing sends automatically.” | `PRODUCT.md:68–73`; `macapp/Sources/PanelView.swift:2587` Send reply control; `lib/keeper_server.py:1268–1270,1412–1445` separates a requested draft from the explicit send endpoint. Scoped to optional reply workflow, not legacy opt-in scripts. |
| Free open-source app, AGPL | Cost field and footer | `LICENSE:1–9,635–642`; `landing/terms.html:67,81` is the legal source, not the old marketing page. No subscription, guaranteed free inference allowance or future-price promise introduced. |
| Own key and provider costs | Cost: “Sorting needs your own Jev key, billed by TypeSafe.” Drafts use tool account/billing | `lib/jev.py:28–34,67–95`; `macapp/Sources/PanelView.swift:1618–1637`; `landing/terms.html:73` allocates cost to configured provider. No dollar price or quota claimed. External provider terms remain authoritative. |
| Not notarized by Apple | Install warning before command | `macapp/build.sh:122–127` ad-hoc signing, not notarization; `macapp/install-zero.sh:9–18` records Gatekeeper implications. Installed signature checked read-only, no trust settings changed. |
| Installer may add Homebrew, Python, Node, gws and Claude Code | Install warning, with “Read the installer” route | `macapp/install-zero.sh:94–112,145–157`. Existing tools are respected, Claude is installed only if no listed coding tool exists. “May add” is deliberate. Root `install.sh:32–33,78–87` is source-checkout setup, not the script served by the landing command. |
| Exact install command | Install code block: `curl -fsSL https://zero.headless.com/install \| bash` | `landing/build.sh:4–8` and `landing/nginx.conf:8,24–26`. `/install` redirects to `macapp/install-zero.sh`. No new one-liner invented. |
| Readable installer route | Hero “Read the installer first”; install “Read the installer” | `landing/nginx.conf:28–33`: `/install.sh` points to the readable GitHub source. |
| GitHub source/releases and key route | Destination map in COPY.md; inline install links and footer | `macapp/install-zero.sh:34–40` release repository; `macapp/Sources/PanelView.swift:1622–1637` links to the TypeSafe key console; `landing/privacy.html:8` and `landing/terms.html:8` preserve legal destinations. Implementation routes explicitly listed in COPY.md. |
| Privacy and Terms kept | Privacy inline field + footer | Existing legal files `landing/privacy.html` and `landing/terms.html`; nginx `try_files` serves them. No legal text changed by this slice. |
| Honest hero illustration with four kept items | Hero panel brief + adjacent caption | `macapp/Sources/PanelView.swift:353,490–492,2941` establishes real list/count/control vocabulary. Count, names, subjects and the dated example are fictional. No customer-result or guaranteed short-inbox claim. |

## What is not advertised

- **Automatic morning operation after this installer.** `PRODUCT.md:31–34,80–81` describes desired cadence. `bin/zero:169–229` ships an opt-in scheduling command, and Rules/Schedule UI edits an existing launch agent. `macapp/install-zero.sh` installs and launches but does not call that command, while `macapp/Sources/PanelView.swift:1397` says rescheduling only occurs if it is installed. So scheduling code exists, but unattended operation is not implied as the install default. The page names the manual run button.
- **`npx zero init` / `npx zero add-account`.** `PRODUCT.md:83–90` is desired setup, not the landing installer route. Not included.
- **Zero mistakes, four actual results, speed-up or completion time.** Not evidenced and not included. First runs should be checked.
- **On-device AI, no data shared, blanket security assurance.** False for the configured providers. Concrete fields and warnings are disclosed.
- **A new “Clean inbox” control or invented explanation badge.** The demo is editorial. Real app control names remain Run zero now, Undo, Restore all, Rules and Send reply.

## Shipped-app correspondence

Read-only check against `/Applications/zero.app`, app **1.7.0**, arm64, minimum macOS **26.0**. These source files are byte-identical to `Contents/Resources/payload/` in that installed app (SHA-256):

| File | SHA-256, same for repository and installed payload |
|---|---|
| `lib/review_open_loops.py` | `cf017b7fde5d8040f105be78a3df70a22417740f86f3da7d2078e2d3a207223a` |
| `lib/keeper_server.py` | `2e5081d5da3fdc783025b3955f899c1fa6bf9d9eaa3682e707dd2c009be52afd` |
| `lib/llm.py` | `327d5b534b28d63b7133bade76cc434173953befd1de54ad453b41ffa5a88f5f` |
| `lib/jev.py` | `2b92a45603b6a97a7c142c06655b041d1d62d74766bce9cd3adc6b6f21c38f39` |
| `lib/inbox_zero.py` | `c53a859dc2500c0a227316558ac99b4f6d8994f386baf841189bd3330a9eb46c` |
| `keep-policy.md` | `491f2e2303e3e1787ebfa27e20c9d9c3f8c90396cf451ce72a4077507314c8ab` |
| `bin/zero` | `ad71dbf7852490efc6ad9b346a5e46f8d46fdbe069265a986566946be78e2866` |

Command output is preserved in `shipped-app-check.txt`. Swift UI strings are checked in current sources; architecture/version/signature are checked in the installed binary. The copy audit did not archive, restore, send or grant permissions against the owner's authenticated inbox. Source/bundle correspondence is not a new end-to-end install test. That workflow belongs to the later build/QA slices.
