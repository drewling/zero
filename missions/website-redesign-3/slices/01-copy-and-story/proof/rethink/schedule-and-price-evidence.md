# Source-backed schedule correction and dated price

Checked 2026-09-30 00:50–00:51Z, read-only source. This is an owner-visible proposed story correction, not an approved new promise. No scheduler, installer, app, sign-in or mailbox operation was executed.

## Conditions, not a daily-by-default promise

- `bin/zero:169–229` is the explicit `schedule` command. It writes `~/Library/LaunchAgents/com.drewl.zero.daily.plist`, schedules `bin/zero run` through `StartCalendarInterval`, then calls `launchctl load -w`. A written plist alone is not a successfully loaded agent: lines226–229 distinguish success and a load failure. The development checkout installer only PRINTS `./bin/zero schedule` as a next step (`install.sh:83–87`), it does not run it.
- `lib/keeper_server.py:1890–1897` explicitly says it does not auto-install a schedule the user never set up, and returns if the plist does not already exist. Schedule field changes invoke this updater at2523–2527. Reload errors are non-fatal at1941–1953. A successful settings save therefore does not prove that launchd has loaded a working schedule.
- `macapp/Sources/PanelView.swift:1394–1428` exposes **Settings → Daily routine**, time and days, with the exact condition “if it's installed”. `KeeperModel.swift:274–285` saves those fields. Changing the controls alone does not install the agent.
- `bin/zero:187–201` reads saved time/days with fallback07:00 Monday–Friday. An empty days list schedules every day, not “off”. Source settings defaults agree (`keeper_server.py:1865–1873`). Do not call this universally daily, always-on, immediately enabled or disabled by clearing day buttons.
- On each triggered run, `bin/zero:42–60` reads configured accounts, skips `enabled=false` and executes the keeper for the others. Working Gmail credentials and inference configuration remain prerequisites, just as for manual runs. No claim of successful execution while sleeping/offline, schedule reliability, or missed-run timing is established here.
- Public Mac installer source `macapp/install-zero.sh:145–281` installs dependencies/app and launches it, but contains no `zero schedule` or launch-agent installation in that path. This source inspection does not test a real installer run or assert an authenticated owner's current schedule.

## Every candidate manual-only implication audited

| Location | Existing words/scene | Scoped verdict and minimal proposal |
|---|---|---|
| Approved hero B | Run zero now → Working… and app actor | This is a real immediate-run control, not the word “only”. Preserve approved strings and animation. Do not add an invented scheduler UI to the hero. |
| Hero promise/requirements | Mac app keeps/archives, Gmail/Apple Mail | Does not state frequency. No hero rewrite needed for factual correction. |
| A recovery intro | Start a run from zero's menu bar. The app sorts the Gmail accounts you connect. | True, but readers infer exclusivity from this being the sole run explanation. Add the conditional sentence below beside this sentence. |
| B Rules intro | Run zero from its menu bar to sort connected Gmail accounts. | Also true, not exclusive. Frozen B stays the documented tested rival. Its manual-only inference remains explicitly unresolved if only selected A gains the proposed schedule sentence. |
| Install setup | Open zero, connect Gmail, save key | Do not suggest these steps automatically enable scheduling. Keep install setup unchanged. |
| Optional replies | Drafts never send automatically. | Scoped to reply sending, not mail sorting frequency. Preserve this distinction. |
| Source manual button tooltip | PanelView.swift:2947 says “runs automatically each morning too” | Tooltip is broader than the conditional scheduler implementation. Do not copy it as an unconditional guarantee. |
| Reader answers | All six ask/infer manual-only | Diagnostic inference, not product truth. Retain raw answers and correct the interpretation in the findings. |

**Proposed minimal A addition:** “Scheduled runs need zero's launch agent installed and loaded; set time and days in Settings → Daily routine.” The source-backed setup route is the checkout CLI `bin/zero schedule`, not a new clickable native setting. The page need not instruct a casual visitor to run a second shell command. Tayo should decide whether this conditional fact earns page space. The addition does not claim install-default scheduling.

## Dated price evidence

Authoritative public source: https://docs.typesafe.ai/models, fetched2026-09-30 00:39Z with native webfetch. The page lists **Jev1.13**, model ID `jev-1.13.0`, “$42 / Btok”, and “Outputs free”. Its aliases `jev-latest` and `jev-preview` currently point to1.13. `lib/jev.py:34` selects `jev-latest`. Arithmetic: $42 /1,000,000,000 input tokens = **$0.042 per million input tokens**.

Use a version and check date, link the rate source, retain the visitor's own key and TypeSafe billing. Do not invent cost per inbox, email, month, free tier or a forever rate for a moving model alias. This is the provider's own authoritative tariff, not a measured user invoice or independent cost benchmark.

## Acceptance still owed

A revised copy inventory must count the schedule and tariff words plus all alternate clipboard states. The final rendered page must keep every data field, conditional installer warning, own-key billing and explicit draft-send control. Independent QA and new observations apply to the revised object, not retroactively to the frozen A/B readers.
