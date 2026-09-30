# Truth trace for the two rethink drafts

Updated2026-09-30 01:04Z. Historical A/B rows below retain `SECTION-COPY.md` Draft3 and approved hero provenance. **Owner-selected B now uses `SELECTED-B-COPY.md` Draft4**, with a complete changed-line retrace below. Source/authoring verification is not final rendered acceptance. Frozen Draft3 render inventories passed at `cdfee91`; tightened B rendering remains pending. Detailed prior source trace remains `../truth-trace.md`.

| Requirement / truth | A location | B location | Source and scoped conclusion |
|---|---|---|---|
| Mac app cleaning Gmail inbox, keep action mail/archive rest | Approved hero unchanged | Approved hero unchanged | `PRODUCT.md:9–15,25–34`; `keep-policy.md:8–23`. Intended policy, not error-free classification. |
| Usual email client, Gmail only | Hero requirement plus recovery intro's connected Gmail-account clarification | Hero requirement plus ledger intro's connected Gmail-account clarification | `PRODUCT.md:31–34,74`; `PanelView.swift:490–492`. Apple Mail is a viewing client for the Gmail account, not another supported provider. |
| Manual run, connected accounts | Recovery intro: start a run from menu bar/app sorts accounts | Rules intro: explicit menu-bar run sorts connected Gmail accounts | `PanelView.swift:2941–2947`; `keeper_server.py:294–310,392–412`. No implied install-default schedule. Hero popover keeps exact Run zero now/Working states. |
| AI classification against editable rules | Recovery rules paragraph | Rules intro plus exact source-contiguous Settings/Rules excerpt | `review_open_loops.py:974–998`; `PanelView.swift:1320–1322`. No invented per-email explanation mode. |
| Default action categories and may-archive examples | Recovery policy sentence | Faithful keep-policy.md:8–21 excerpt including Cold outreach; final rendered inventory pending | `keep-policy.md:8–23`. Preserve policy meaning, avoid guaranteed category accuracy. |
| Model can err, check first runs | Recovery before restore mechanics | Rules intro | Classification source is fallible. This is a user action, not security assurance. |
| Starred untouched by sorting | Recovery rules paragraph | Rules intro | `review_open_loops.py:152–155` excludes starred from sorting query. |
| Uncertain thread kept | Recovery rules paragraph | Rules intro | `review_open_loops.py:1070–1099`. Not every error is necessarily recognized as uncertain. |
| Nothing deleted | Recovery mechanics | Recovery mechanics | Archive path `review_open_loops.py:1785–1793` adds recovery label/removes INBOX, does not delete messages. |
| All Mail searchability + dated label | Recovery mechanics | Recovery mechanics | `inbox_zero.py:5–6,225–238`; `review_open_loops.py:1789–1793`. One detailed explanation. Approved hero's dated folder is an editorial visual cue, not a new Finder app mode. |
| Individual/day recovery in zero Undo | Recovery mechanics and source-faithful facsimile | Recovery mechanics and same facsimile | `PanelView.swift:1017–1107,1151–1175`; `keeper_server.py:535–599,647–697`. Batch Restore all exact, individual tray-up icon exact tooltip. No invented Restore in Gmail/Finder. |
| Apple Silicon/macOS26+ | Approved hero only | Approved hero only | `macapp/install-zero.sh:61–79`; `macapp/build.sh:22`, installed architecture/min version previously checked. Do not repeat in ledger. |
| Browser Google sign-in/no password | Google sign-in row | Google sign-in row | `OnboardingView.swift:120`; `keeper_server.py:1502–1506,1542–1558` uses OAuth/gws. |
| Google unverified app warning/incomplete review | Google sign-in row | Google sign-in row | `OnboardingView.swift:104–107`. Plain warning, no instruction to bypass or guaranteed review date. |
| No zero server receives email | Sorting data row | Sorting data row | Local service `main.swift:100–110`, `keeper_server.py:2646–2652`; direct TypeSafe endpoint `jev.py:8,33`. Does not imply nothing leaves device. |
| Sender, subject and up-to160-character preview to Jev | Sorting data row | Sorting data row | `review_open_loops.py:640,691,974–998`. Preview limit is classification-only, not a universal bound on draft context. |
| Both reply-history signals | Sorting data row, plain meanings | Same row | `review_open_loops.py:987–993`: last_from_owner/replied_before. Latest message and prior reply to sender, not a full history-content claim. |
| Rules + learned preferences to Jev | Sorting data row | Same row | `review_open_loops.py:994–997`; learned context conditional. Existing wording does not claim all preferences always exist. |
| Optional draft through existing coding tool | Optional drafts row | Same row | `llm.py:2–12,22–55,76–87`; `PanelView.swift:1711`. Claude Code or another supported installed tool, not universal arbitrary compatibility. |
| Draft context: previews/sent samples/writing prefs/saved profile | Optional drafts row | Same row | `keeper_server.py:1288–1307,1314–1349,1358–1400`. No claim only metadata leaves Mac. |
| Explicit Send reply, no automatic draft sending | Optional drafts row | Same row | `PanelView.swift:2587`; `keeper_server.py:1268–1270,1412–1445`. Wording **Drafts never send automatically** is scoped to this UI workflow, not all opt-in legacy scripts. |
| Own Jev key, TypeSafe billing | Sorting cost row | Same row | `jev.py:28–34,67–95`; `PanelView.swift:1618–1637`; `landing/terms.html:73`. No dollar/month or guaranteed rate claimed. |
| Authoritative current rate source | TypeSafe pricing link | Same link | Public `https://docs.typesafe.ai/models`, verified2026-09-29. `cost-and-control-check.md` records current rate/model and the failed guessed /pricing route. |
| Free app/open source/AGPL | Sorting cost row after provider billing, footer license link | Same | `LICENSE:1–9,635–642`; `landing/terms.html:67,81`. Not free inference. Footer license navigation isn't a second cost explanation. |
| Draft account/billing | Optional drafts row | Same | `llm.py` uses selected installed tool; provider cost allocated in `landing/terms.html:73`. Not zero subscription billing. |
| Not notarized | Installer row, before actual command | Same | `macapp/build.sh:122–127` ad-hoc signing, not notarization. Do not call unsigned. |
| Conditional Homebrew/Python/Node/gws/Claude footprint | Installer row | Same | `macapp/install-zero.sh:94–112,114–156`. Existing tools respected, Claude installed only if no supported coding tool exists. |
| Exact executable command | Terminal | Terminal | `landing/build.sh:4–8`, `landing/nginx.conf:8,24–26`. `curl -fsSL https://zero.headless.com/install | bash` unchanged. No command executed in proof. |
| Read installer route | Approved hero source-reading link | Same | `/install.sh` in `landing/nginx.conf:28–33`. Install CTA targets material ledger before command, not a new download endpoint. |
| Setup/key/release/source routes | Terminal setup/footer | Same | Connect Gmail, key in Settings → Sorting engine, `https://console.typesafe.ai/keys`, actual source/release repo. No aspirational npx init/add-account. |
| Privacy/Terms destinations | Sorting-data inline privacy + footer links | Same | `/privacy.html`, `/terms.html` remain unchanged legal pages, no legal rewrite in this slice. |
| Honest examples, no owner mail exposed | Approved hero caption + readable Undo facsimile caption | Same, plus faithful Rules illustration | Five visible fictional archived rows/address/ages in an eight-item batch with a scrollbar, not a measured customer result or real screenshot. No live inbox read needed. |

## Selected B Draft4 changed-line retrace

Owner chose risk-first B at00:58Z (`qitem-20260930005833-05ef6df1`). Only B is being tightened; A and original reader evidence stay archived. New author total: hero104 + prose274 + shared objects56 + Rules110 + alternate copy statuses5 = **549**. The Rules excerpt and every sorting/draft field remain intact.

| Changed visitor line | Source / verification | Truth preserved or limitation |
|---|---|---|
| Read connected Gmail in Gmail or Apple Mail | `PRODUCT.md:31–34,74`, `PanelView.swift:490–492` | Gmail account viewing, not Apple Mail accounts or other providers. |
| Sent to TypeSafe (Jev), complete field list | `review_open_loops.py:640,691,974–998`; direct endpoint `jev.py:8,33` | Sender, subject, <=160-character preview, last-message-owner signal, previously-replied-to-sender signal, rules, conditional learned preferences. No field cut. |
| No zero server receives your email, separately bold | `main.swift:100–110`, `keeper_server.py:2646–2652`, direct TypeSafe endpoint | Retained disclosure explicitly paired with outbound TypeSafe recipient, not a promise that nothing leaves the Mac. |
| Optional drafts via installed tool, its account/billing; Sent to your coding tool's provider | `llm.py:2–12,22–55,76–87`; `keeper_server.py:1288–1400`; `landing/terms.html:73` | Existing tool context/billing and full previews/samples/preferences/profile list retained. Supported tool compatibility, not universal arbitrary CLI support. |
| Review before Send reply; Drafts never send automatically | `PanelView.swift:2587`, `keeper_server.py:1268–1270,1412–1445` | Explicit send action in optional UI drafting workflow. Not a claim about every opt-in legacy script. |
| Your Jev key, billed by TypeSafe | `jev.py:28–34,67–95`, `PanelView.swift:1618–1637`, terms73 | Personal inference key/cost remains primary, not zero subscription or free sorting. |
| Jev1.13 at$0.042/M input tokens, outputs free, checked30Sep2026 | `https://docs.typesafe.ai/models`, native fetch2026-09-30 00:39Z, and `lib/jev.py:34` | Dated/versioned provider tariff. Moving `jev-latest` currently resolves1.13. No per-inbox/month or permanent-rate promise. Arithmetic/source in `schedule-and-price-evidence.md`. |
| Free, open-source app (AGPL-3.0) | LICENSE1–9,635–642; terms67,81 | Free app distinguished from billed inference; no removed license fact. |
| Google browser sign-in/password/app-review warning | `OnboardingView.swift:104–120`; OAuth/gws path `keeper_server.py:1502–1558` | All disclosures retained despite shorter wording; no bypass instruction. |
| Installer: non-notarized and conditional dependencies | `macapp/build.sh:122–127`, `macapp/install-zero.sh:94–156` | Homebrew/Python/Node/gws remain conditional. Claude added only if no supported tool installed. No unsigned/tiny-footprint guarantee. |
| Use Run zero now; starred untouched, uncertain inbox, AI mistakes | `PanelView.swift:2941–2947`, `review_open_loops.py:152–155,1070–1099` | Immediate sorting example remains true. Does not say only manual. No schedule promise added. |
| Searchable All Mail, dated label, individual/day restore | `inbox_zero.py:225–238`, `review_open_loops.py:1785–1793`, `PanelView.swift:1017–1175` | Restores exact recovery truth, explicitly adds searchability. No delete and no invented Finder/Gmail Restore controls. |
| Canonical public privacy/terms/installer routes | `landing/nginx.conf:28–33`, unchanged legal pages; designer39aa729 reports read-only public statuses | Root-relative proof404 defect is fixed in designer build; independent final GET/redirect checks remain pending. Labels/command unchanged. |
| Copied / Copy manually: press Command-C. | Public fault checks exposed silent handler. Designer39aa729 supplies shared status/selection implementation | Five authored state words included even before visible. Real denial/unavailable/focus/selection recheck still required, not verified by wording. |

### Schedule proposal intentionally outside page B

Daily routine time/day settings do not create an agent. `bin/zero:169–229` must install and successfully load it. `keeper_server.py:1890–1897` returns without an existing plist, and schedule save reload errors are non-fatal. No daily/default/always-on wording enters COPY-B. The approved hero Run/Working states stay untouched. Optional exact conditional wording remains owner-visible in `SELECTED-B-COPY.md` and `schedule-and-price-evidence.md`, with a new count required if approved. Original reader manual-only inference remains a diagnostic limitation, not a false product assertion adopted into the copy.

## Boundary status

- Historical Draft3 material map matches frozen `cdfee91` inventories A474/B544, including exact110-word Rules excerpt. Tightened B retains all material fields, with new recipient grouping/rate/statuses as traced below. Its final rendering has not yet been observed.
- No landing edit, push, release, Gatekeeper override, installer execution, Gmail permission grant, archive/restore/send or real inbox screenshot occurred in this pass.
- “Said once” means one canonical material explanation. Approved hero promises, real UI labels and legal navigation remain, but repeated feature paragraphs and repeated demo examples are cut. Literal repeated-word removal would conflict with the approved hero and source-faithful controls, so this interpretation is disclosed rather than hidden.
