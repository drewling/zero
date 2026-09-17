# Distribution plan

_Planning snapshot: 2026-09-17. This document specifies work, not shipped behavior. No implementation is part of this plan._

> **Superseded on the central question. Read `EASY_INSTALL_PLAN.md` first.**
>
> This plan makes a **local source build** the default install, on the reasoning that
> building locally avoids the downloaded-executable quarantine path. That reasoning is
> sound, but the premise turned out to be unnecessary: measured on macOS 27.0
> (26A5388g), a release fetched with `curl` carries **no** `com.apple.quarantine`
> attribute anywhere in the bundle, because that flag is applied by the *downloading
> application* and command-line tools don't set it. Launching it through `open`
> succeeds with no Gatekeeper denial logged.
>
> So the prebuilt app installs cleanly via `curl | bash` with no Xcode, no SDK, and no
> build wait, and the extra step here of downloading a DMG purely to extract
> `client_secret.json` is unnecessary (the release already ships it).
>
> **What shipped instead:** prebuilt is the default; `zero.headless.com/install` 302s to
> `macapp/install-zero.sh` on master so it is never stale; each release publishes
> `zero.dmg.sha256` and the installer refuses a DMG that doesn't match.
>
> The rest of this document is still worth reading. Its insistence on failing visibly
> rather than silently is exactly right, and the hardened installer implements it:
> fatal checks for Intel and macOS < 26, prerequisite failures reported instead of
> warned past, and a signature failure treated as an error rather than "expected".

## Decision

**Make a local source build the default one-command install. Keep the prebuilt DMG as an explicit faster alternative, not the fallback chosen silently. Never require a paid Apple Developer account.**

The supported target remains **Apple Silicon, macOS 26 or later**, with a compatible macOS SDK. A source build avoids the normal downloaded-executable quarantine path. It does not defeat malware protection, device-management policy, damaged signatures, missing SDKs, or future macOS changes. Do not promise that it does.

The default installer must also obtain the **bundled Desktop Google OAuth client from the matching official release**. Today a clone does not contain that client. Building the repository alone therefore does not deliver the advertised first-run experience.

For the first implementation, download the exact release's DMG, mount it read-only, copy **only** `Contents/Resources/payload/client_secret.json` to installer staging, validate it, and pass its path through `ZERO_CLIENT_SECRET` to the local build. Never launch or install that downloaded app on the source path. This reuses the existing distribution of the client without putting the JSON into public git. It costs an extra download. Later, a policy-reviewed standalone client resource can replace extraction without changing onboarding. A resource download is not an executable Gatekeeper exemption: inspect the finished local bundle for inherited quarantine and fail visibly if unexpectedly present.

**Use bundled Google sign-in by default while it is available. Offer bring-your-own Google client as an explicit advanced escape hatch, including at the cap.** Do not make every stranger create a Cloud project to avoid maintaining a release resource. Do not quietly fall back to that flow after a corrupt download.

Judgment is **Jev using the user's own key**. Drafting is optional and uses **the user's already-installed, authenticated `claude`, `codex`, or `opencode`**. Do not install Claude, create a subscription, or switch drafting providers without consent. With no drafting CLI, sweeping still works.

The honest promise is **one command to install and open guided setup**, not one command to authorize Google, obtain a Jev key, approve OS prompts, and finish a sweep unattended. With an unverified shared Google project capped at 100 new users in total, “any stranger can connect” is false. That is a distribution limit, not an installer bug.

## What the repository does now

Read first: `README.md`, `macapp/install-zero.sh`, `macapp/build.sh`, `docs/GOOGLE_VERIFICATION.md`, `docs/SETUP.md`, `lib/llm.py`, onboarding/auth in `lib/keeper_server.py`, `macapp/Sources/OnboardingView.swift`, and `macapp/Sources/Updater.swift`. Also checked `bin/zero`, `main.swift`, and `KeeperModel.swift` for integration points.

| Current behavior | Distribution consequence |
| --- | --- |
| Installer downloads `releases/latest/download/zero.dmg`, installs Homebrew/Python/Node/gws/Claude, and only warns on unsupported hardware or OS. | Can install an app that cannot launch. Installs a drafting product the user did not choose. |
| Installer removes the existing app before copying the new one. Prerequisite failures only warn. Quarantine failures are suppressed. Failed signature verification prints “ad-hoc signature (expected)”. | A failed install can remove a working app or claim success with broken prerequisites/signature. Ad-hoc signatures must still verify. |
| `build.sh` targets `arm64-apple-macosx26.0`, uses `swiftc`, `swift`, `iconutil`, `rsync`, and ad-hoc `codesign`. Signing failure is nonfatal. | OS version alone is not proof of a compatible SDK. Build success is not yet a verified runnable artifact. |
| `build.sh:72` reads `ZERO_CLIENT_SECRET` or the maintainer's `~/.config/zero-build/client_secret.json`. Missing client merely prints a note. | A stranger's source build has no built-in Google sign-in. This must be fixed before source becomes the default. |
| README says production-unverified cannot grant restricted Gmail scopes. SETUP and the verification decision say production-unverified works within the cap. The verification table still says Testing. | Contradictory instructions send users into the seven-day expiry trap. Treat production-unverified as the supplied project state, not as a fresh console audit. |
| Onboarding checks only executable presence for Python/gws/Claude. Missing Python suggests `xcode-select --install`. | Presence is not runtime compatibility, Google auth, Jev readiness, or drafting readiness. CLT is not a reliable Python installation instruction. |
| Google connect has a browser fallback link, Cancel, a 180-second timeout, profile verification, duplicate-account detection, and API-enable recovery. | Preserve these useful pieces. Add distinct cap, policy, denied-scope and client errors rather than a generic retry loop. |
| Google clients/accounts currently live under shared `~/.config/gws`; `_kill_stray_auth` kills processes matching `auth.login`. | zero can interfere with unrelated gws users. Use zero-owned config directories and kill only zero-owned process groups. |
| `main.swift` creates the menu icon before server boot, auto-opens first-run setup, supports Finder reopen and ⌥⌘Z, and writes `~/Library/Logs/zero-launch.log`. | Invisible failure has partial protection already. Extend it, do not describe the app as having no first-run UI. A hidden icon must not be the only recovery entry. |
| Backend startup/state polling eventually produces a transient “Can't reach the zero server” toast. Payload seeding uses many `try?` operations. | A persistent startup error needs a fix and logs even when Python never starts. |
| `llm.py` has provider argv data but falls back to Claude when the selected provider fails or Jev is selected for text. Concurrent Jev key code reads environment/repo `.env`. | Separate judgment from drafting explicitly. Finder/launchd do not reliably inherit shell keys. Do not silently switch a user's model vendor. |
| Updater checks every six hours, requires a click to install, downloads `latest`, replaces the app, strips quarantine and reopens it. | Source installs would silently become downloaded-binary installs. Release races, signature checks, rollback and visible helper failure need work. |

## The install command and its contract

Keep one bootstrap entry point: `macapp/install-zero.sh`. Its proposed default is `--source`; `--binary` is opt-in. A release should publish a complete command with an actual immutable commit in place of `<release-commit>`:

```bash
stage="$(mktemp -d)" && curl -fL --retry 3 "https://raw.githubusercontent.com/drewling/zero/<release-commit>/macapp/install-zero.sh" -o "$stage/install-zero.sh" && /bin/bash "$stage/install-zero.sh" --source
```

**This is a specification, not a command supported by today's installer.** Generate the real copyable command in the release/README when the work below ships. Downloading the complete script before execution avoids executing a partial streamed response. Document an inspect-before-running alternative. The user still trusts the publisher of the script. TLS and a hash from the same compromised release do not prove publisher identity.

Installer contract:

1. Acquire a per-user install lock. Print the selected release, source/binary mode, target directory and what prerequisites will be installed. Never operate on the user's existing checkout.
2. Hard-stop unsupported OS/hardware. Detect Rosetta translation and tell an Apple Silicon user to use a native Terminal rather than claiming their Mac is Intel. Check free space, connectivity and destination writability.
3. Detect CLT/SDK readiness, not just `xcode-select -p`. Run a small SwiftUI/macOS-26 API compilation probe. If missing, open the normal Apple installer and print “Finish installing Command Line Tools, then rerun this same command.” Handle license/setup errors with the exact Apple tool output. Do not pretend this is unattended.
4. Reuse compatible Python and gws. If missing, offer the documented package-manager setup and report each result. Node is needed only if installing gws through npm. Prefer a user-owned prefix on npm permission errors, never `sudo npm`. Do not install or upgrade any drafting CLI. Pin a tested gws version and document a tested version range for existing installations.
5. Resolve one release to one commit, source archive, DMG/client resource, version and checksums. No mixture of moving `master` and `latest`. Fetch into `~/Library/Caches/zero/install/<release>/`, outside Documents/Desktop/Downloads. A source archive avoids requiring git merely to install. Validate archive paths, expected top directory and hashes before extraction. Never execute arbitrary archive hooks.
6. Source mode: extract the matching official DMG's installed-client JSON only, validate its Google endpoints/client identity and build with `ZERO_CLIENT_SECRET` pointing to staging. A missing release client is a release-packaging failure with Retry or explicit Use my own client, not silent success. A deliberately offline developer build may opt out and clearly declare BYO required.
7. Build locally. Require a valid ad-hoc signature and expected bundle ID, architecture, minimum OS, version and payload. Inspect quarantine attributes on the complete staged bundle. Stop on failure and preserve the log. Do not report an invalid signature as “expected”.
8. Stage beside the destination, preferably `~/Applications/zero.app` for a no-admin install. Preserve a pre-existing installation location only if writable and explicitly identified. Never clobber an unrelated app or symlink. Keep the old bundle as a rollback copy until the new app and server prove healthy.
9. Install a small `~/.local/bin/zero` launcher pointing to the installed runtime, not the disposable source checkout. Print its absolute path because shell PATH may not include it. Do not silently edit shell startup files. It must expose doctor even if full onboarding is incomplete.
10. Launch by absolute path and wait up to 30 seconds for a launch receipt and authenticated local health response with the expected version. `open` returning zero is not proof. On failure print the exact log path, show a native error if possible, return nonzero, and leave a copyable doctor command.
11. Print separate outcomes: “Installed”, “App running”, “Setup required”, “Ready to sweep”. Never print “Done” for unmet required checks. Clean only installer-owned staging, unmount volumes on every exit, and preserve diagnostic logs. Re-running resumes safely and never resets accounts, keys, policy or schedules.

### Why not make DMG plus xattr the default?

| Path | Benefit | Cost / limit | Decision |
| --- | --- | --- | --- |
| Local source build | Locally generated executable avoids the ordinary browser-download quarantine route. No paid signing/notarization service. Source release can be inspected. | Requires CLT, suitable SDK, disk/time and possibly an interactive Apple installation. Not bit-for-bit reproducibility by default. Needs the separate OAuth resource above. | Default after these gates ship. |
| Prebuilt DMG + scoped quarantine removal | Fast, no Swift toolchain, client already bundled. | Asks the user to override a security boundary. Attribute removal alone is not proof that current/future macOS will launch the app. MDM, XProtect, signatures and OS policy can still block it. | Explicit `--binary` alternative with informed consent and launch verification. |
| Manual Finder drag | Familiar. | Downloaded ad-hoc app gets an unknown-developer/notarization warning. A menu-bar app makes launch failure easy to mistake for no effect. | Advanced instructions, not the primary CTA. |

For binary mode, show the trust explanation before touching attributes. Verify the downloaded artifact and staged ad-hoc signature, then remove **only** `com.apple.quarantine` with `/usr/bin/xattr -dr com.apple.quarantine "$APP"` on zero's staged app. Read back attributes. Do not broadly run `xattr -cr`, disable Gatekeeper, remove provenance attributes, disable SIP, or suppress a malware warning. If macOS blocks an unidentified/unnotarized app, the supported user override is **System Settings → Privacy & Security → Open Anyway**, after attempting to open that specific app, and only if the user trusts it. Do not recommend old Control-click folklore as the macOS 26 solution. A “will damage your computer” or managed-device block is a stop-and-investigate condition, not an instruction to bypass it. [A1][A2]

A `spctl` rejection of an ad-hoc build is diagnostic, not by itself proof that a locally built app cannot run. `codesign --verify` tests signature integrity, not notarization or safety. The acceptance test is a launch on a clean target Mac under its normal security settings. We have not performed that test for this document.

## Every step from the repository to a first sweep

Steps 1–18 are the ordinary path. G1–G8 below replace step 10 when the user chooses their own Google client. Each failure must leave the user at the relevant step with entered non-secret choices intact.

| Step and user action | Failure modes | Exact mitigation / visible result |
| --- | --- | --- |
| 1. Read the GitHub Install section. | Unsupported Intel/older macOS, misleading “nothing leaves your Mac”, expectation of free inference or no prompts. | Put Apple Silicon/macOS 26+, CLT requirement, BYO Jev key/account, optional existing drafting CLI and shared Google cap immediately above the command. State that thread content goes to Jev and drafting content to the chosen CLI's configured provider. |
| 2. Open Terminal, paste one command. | GitHub/DNS/TLS/proxy failures, captive portal, partial script, command pasted incorrectly. | Full download before execution, bounded retries and visible URL/status. “Download failed. Check your connection or proxy, then rerun this command.” Never continue on empty/partial content or disable TLS validation. |
| 3. Confirm bootstrap prerequisites if needed. | No CLT/Homebrew, no admin permission, Apple installer waiting, license not accepted, outdated SDK. | Describe each required install before starting it. For CLT, show the Apple prompt and the rerun instruction. Offer manual dependency instructions or binary mode if toolchain installation is unavailable. No paid Apple membership is needed. If device policy prohibits both, state unsupported. |
| 4. Let Python/gws setup finish. | npm EACCES, Node missing, incompatible Python/gws, executables only visible in shell, third-party `xattr`. | User-owned npm prefix, compatible interpreter test, gws version/auth-command probe. Persist resolved paths in zero-owned configuration and test from GUI/launchd environment. Use absolute system security tools. A missing required dependency stops before launch. |
| 5. Wait for source + client retrieval and build. | Missing release assets/client, mismatched versions/hash, malformed archive, compiler failure, disk full, signing error. | Fail with stage name and log path. No install replacement yet. Retry resumes that release. No unaudited switch to moving master, prebuilt code or BYO OAuth. |
| 6. Let installer copy the app and launcher. | Read-only `/Applications`, space/path issues, old app running, parallel installer, copy interrupted. | Default user Applications, install lock, graceful quit, same-volume staging plus recoverable backup. Preserve old app and data. “Install not changed. Free space / quit zero / choose writable destination, then Retry.” |
| 7. See zero open setup. | Gatekeeper, bad signature, crash, icon hidden by notch/menu manager, offscreen display, no panel. | Verify launch receipt. Auto-open setup on active screen. Print “Reopen zero from Spotlight, or press ⌥⌘Z.” Handle shortcut collision and provide Finder reopen independently. If process cannot launch, installer provides OS-specific error and doctor/log command. |
| 8. Wait for local readiness checks. | Python spawn/import failure, payload copy failure, port 8765 occupied, stale server from old version, malformed state, backend crashes. | Persistent native “zero couldn't start” view independent of backend, with Retry, Run diagnostics and Open logs. Authenticate/version-check loopback server; never attach to an arbitrary listener or kill it. Choose a negotiated free port or report the collision with a fix. No permanent spinner. |
| 9. Review privacy and enter own Jev key. | User has no key/access, wrong/expired key, whitespace paste, no credits, offline/DNS/TLS, rate limit, service outage or incompatible response. | Link to TypeSafe's key/account entry from verified vendor documentation; do not invent a console URL or promise instant access. Secure input + “Test connection” using synthetic non-mail data. Distinguish auth, billing, 429/retry time, network, 5xx and schema failures. Retain settings, block sweep, offer Retry/Replace key. Never fall back to another paid judgment engine silently. |
| 10. Choose Connect Google, using the named bundled client. | Client missing/revoked/wrong type, cap reached, account under Workspace policy/Advanced Protection, shared project misconfigured. | Show client provenance and account choice. Missing packaged client means repair install; cap means BYO or wait for verified service. Workspace/security blocks mean contact admin or use another permitted account. Do not label all 403s “enable API”. |
| 11. In browser, select the intended Google account. | Wrong browser profile/account, popup does not open, localhost redirect fails, user cancels, consent times out. | “Open sign-in page” fallback and Cancel remain visible; open a new flow on Retry, never reuse an expired authorization URL. Explain the loopback callback. Verify returned profile email and let the user confirm it. No need to open a public port. |
| 12. Read Google's unverified-app warning. | User understandably refuses, Advanced option absent, lookalike page, policy hard block. | Before browser launch say: “Google has not verified zero's Gmail access. Continue only if you trust this project. On Google's page choose Advanced → Go to zero (unsafe), then review access.” Check the real Google domain and expected app/client. Provide Cancel/BYO/help. If no proceed link, do not promise one or recommend weakening account security. |
| 13. Grant Gmail + identity consent. | User declines Gmail permission, API disabled, insufficient scope, token persistence fails, wrong account, duplicate account. | Verify identity, granted capabilities and a Gmail profile/read call before marking Connected. “Gmail access wasn't granted. Reconnect and approve the Gmail permission.” For bundled-project API failure, maintainer issue + BYO option, not a console link the user cannot administer. Duplicate account offers Reconnect, not a second entry. |
| 14. Return to zero and see connected account status. | Token expired/revoked, Tests issued with seven-day life, credentials under unrelated gws client, stale dashboard, disk write failure. | Per-account Connected / Reconnect required / Failed state and last checked time. Save atomically in zero-owned directories with restrictive permissions. Never reuse someone else's gws config silently. Show token-lifetime warning if known or user-declared Testing; otherwise say publishing status unknown. |
| 15. Pick optional drafting CLI, or Skip drafting. | No CLI, several installed, found binary not logged in, wrong model ID, GUI PATH differs, auth prompt hangs. | Auto-detect executable paths but ask user to choose when ambiguous. “No drafting agent found. Sweeps still work. Install and sign into Claude, Codex or OpenCode later.” Keep Reply disabled with Set up drafting action. Test chosen CLI with a synthetic prompt and timeout. Show exact provider's login/help action, preserve user's existing setup. |
| 16. Review keep policy and first-run choices. | Huge backlog, unexpected bulk archive, auto-run before consent, unsafe defaults, unreadable policy. | Default to ordinary sweep, offer preview, explain recovery label and Undo. Backlog date-based archive is a separate opt-in, skippable operation, never required to unlock first sweep. No automatic mutation merely because onboarding ends or panel opens. |
| 17. Click Run zero now. | Preflight becomes stale, Jev fails mid-run, Gmail read/write quota/network errors, lock busy, cancel/crash, partial mutation, malformed responses. | Recheck required capabilities. Show phase + account + counts + heartbeat. Bound retries; expose Cancel. Classification failure keeps affected mail and marks run incomplete, not “0 archived” success. Persist an undo journal/recovery label before reporting each mutation. Handle per-account failures separately and never count unacknowledged writes as archived. |
| 18. Read a successful result and confirm Gmail/Undo. | Empty inbox mistaken for failure, all mail legitimately kept, failed state refresh, counts disagree, recovery label absent. | “Sweep complete: N reviewed, K kept, A set aside, 0 failed” with account/time and View in Gmail/Undo. Empty inbox explicitly says “0 threads in inbox”. All kept is success only after real reads/classification. Partial run says “Incomplete”, with affected count/retry action. Show last successful sweep separately from last attempt. |
| 19. Optionally draft a reply. | Missing CLI/auth/model, timeout, quota, tool permission prompt, empty output, provider fallback. | Fail only drafting. Keep existing draft text, show selected engine/model and fix. Never auto-install, silently reroute, send, or let model-generated text execute tools. Sweep remains usable. |
| 20. Optionally enable a daily schedule and notifications. | Notifications denied, Mac asleep/offline/logged out, launchd environment lacks paths/keys, job disabled, stale auth later. | Schedule opt-in after first success. Explain this is local, not an always-on hosted service. Show next planned run, last attempt, last success and failure. Notification denial is advisory. Persist failure in app regardless of notification permission. Verify launchd context with a dry preflight, not an unsolicited real sweep. |

## Google OAuth: default, cap and BYO

### The warning is real

Google documents that unverified apps requesting sensitive/restricted scopes can show a warning and have **100 new users in total** until verification. This is not 100 concurrent installs or 100 users per month. Removing users, reinstalling zero, rotating the client secret or adding another client within the project does not create an honest scaling strategy. Each connected Google identity can consume capacity, so a person with several accounts is not one guaranteed slot. [G1]

Publishing External → **In production** removes the specific Testing seven-day refresh-token rule. It does not verify the app or guarantee a perpetual token. Users can revoke access; password changes involving Gmail scopes, inactivity, token limits, Workspace session policy and other conditions can invalidate tokens. Always support per-account reconnect. [G2]

Do not call “Go to zero (unsafe)” safe merely because it is expected. Explain what Google has not reviewed, the requested scope and the data path. `gmail.modify` is a broad restricted scope, not an archive-only permission. The user must decide whether to trust the application. Branding verification alone does not resolve restricted-scope verification.

### Bundled-client availability

Keep one dedicated project for zero, as now, not an unrelated shared business project. Maintainer release checks must verify actual publishing status, API enabled, declared/requested scopes, support contact and remaining audience headroom in the console. No claim here that we inspected that private console or know the current count. Do not assume there is a public unauthenticated quota API suitable for doctor.

At a confirmed cap block, show:

> zero's shared Google sign-in has reached Google's unverified-app user limit. Reinstalling will not fix this. Use your own Google Cloud client, or wait for verified sign-in. Your existing local data is unchanged.

If Google only provides ambiguous `access_denied`, say “Google did not complete sign-in” and show possible causes plus sanitized details. Do not falsely diagnose a cap. Offer BYO on the first unsuccessful attempt. Existing grants may continue subject to Google's policies; do not promise that deleting/reconnecting preserves a slot. Warn maintainers well before the cap, for example at an internal operational count of 80, not as a new Google limit.

### Should the Desktop client JSON be committed?

**Not in this change. Prefer the existing official release bundle as the client resource; do not present it as confidential.** A desktop client is a public OAuth client. Google says installed applications are assumed unable to keep secrets; RFC 8252 says a statically embedded secret cannot authenticate a native app as confidential. Keeping it out of git does not stop extraction from today's DMG. [G3][G4]

That technical fact is not blanket legal permission to publish credential JSON in a source repository. Google's API terms and OAuth credential-protection guidance must also be considered. Do not assert “Google's ToS explicitly allows committing this file” without a policy basis specific to installed/public clients. Nor claim every distribution of a native client violates the terms. The current installed-client distribution is the documented technical model; public source publication requires a deliberate maintainer policy decision, preferably confirmed with Google, rather than an accidental leak exception. [G5][G6]

The practical risks are the same whether an attacker reads git or extracts the DMG: they can imitate the app's OAuth identity, induce other users to authorize, consume scarce new-user capacity, consume project API quota using legitimate grants, damage the project's reputation, or cause suspension/revocation. **The client JSON alone does not grant access to anyone's mailbox.** An attack still needs valid user authorization/tokens or another flaw. PKCE/state/loopback validation defend a flow against interception, not against all client impersonation or cap exhaustion. Audit the actual pinned gws flow instead of relying on the build script's PKCE comment.

Mitigations: dedicated project/client, minimal scopes, system-browser OAuth with PKCE and state validation, validated loopback redirects, release provenance/checksums, abuse/quota monitoring, a maintainer incident/rotation playbook, and user-owned-client fallback. Never ship refresh/access tokens, Jev keys, service-account keys, or a Web client secret. Forks should create their own app identity rather than market themselves under zero's client. These controls reduce risk; none makes a publicly distributed client secret confidential or prevents determined cap exhaustion.

If source publication is approved later, commit only the dedicated Desktop client as an explicitly public distribution resource with a narrowly scoped secret-scanner allowlist. Keep token/key leak checks strict. This would simplify the installer, but it would not solve the cap. Do not rotate through projects to evade Google's user limits.

### BYO path, fully enumerated

BYO removes dependence on **zero's** shared cap and revocation, not Google's policies. It is the durable advanced/free route, not foolproof mainstream onboarding.

| Step | User action | Failure and mitigation |
| --- | --- | --- |
| G1 | In zero choose Use my own Google client, then open Cloud Console. | Account cannot create projects or is organization-restricted: show that an authorized project/admin is required. A different permitted personal account is an option, not a security bypass. |
| G2 | Create a project or deliberately select one they own. | Wrong project/account: keep project name/ID visible throughout instructions; do not modify a shared production project by default. |
| G3 | Enable Gmail API in that project. | `SERVICE_DISABLED`/propagation delay: link to that project's API page, then Retry with bounded wait. Do not require billing merely by assumption. |
| G4 | Configure Google Auth Platform app information, support/contact email and External audience. | Internal audience excludes outside accounts: explain Internal is only appropriate for a permitted organization-only setup. Missing fields require completing the displayed console step. |
| G5 | Declare exactly the Gmail + identity scopes zero requests, then set Audience → Publishing status → In production. | Testing is not production. If intentionally left in Testing, add each test user and accept seven-day reauthorization for Gmail. For durable use publish, then reconnect to obtain a fresh production grant rather than assuming an old token changed. |
| G6 | Create an OAuth client of type Desktop app and download its JSON. | Web/service-account/API-key file: reject it explicitly with “Create a Desktop app OAuth client.” Do not accept arbitrary auth/token endpoints from pasted JSON. |
| G7 | Import the JSON into zero and confirm the project/client identity. | Invalid/truncated JSON or inaccessible file: keep the error inline and let the user retry. Store a zero-owned copy, not a replacement for global gws credentials. Never ask them to paste it into a public issue. |
| G8 | Return to steps 11–14: sign in, review warning, grant scope, verify Gmail access. | Their project may still show the unverified warning/cap or account-policy restrictions. Explain that production is not verification. Reconnect this account alone on failure. |

Do not require an agent CLI to create the Google project. A “get help from your agent” prompt may remain secondary, but cannot be the only explanation or presume Claude is installed.

### What a future hosted $4.99/month tier must solve

A price and a backend do not remove Google's warning or audience cap. Before promising scalable sign-in, the operator must complete the applicable OAuth app/restricted-scope verification and, where required by the actual data handling, security assessment. The plan must account for Jev processing Gmail content off-device even in the desktop edition. Do not assume a “local app” assessment exception while transmitting restricted data to an external service. Confirm the architecture and current requirements with Google/assessor, including user-data and Limited Use obligations. Historical repo quotes such as ~$1,800/year are not a current budget. [G7]

The hosted tier also needs safe token storage, account isolation, revocation/deletion, privacy and retention disclosures, explicit third-party processor disclosures, abuse controls, operational monitoring, quota management and support. Validate whether $4.99 covers those costs rather than promising it does. Decide whether the hosted product uses a separate verified client/project with a deliberate migration path. It cannot inherit verification by sharing a name or merely moving existing users to a server. Apple paid signing remains unnecessary for the local-source distribution path and is not part of the tier.

## Jev and drafting are separate capabilities

### Judgment setup

Use `JEV` as a supported environment override for developers, but do not make shell exports the consumer setup. Specify one shared resolver for app, CLI and scheduled runs. For the first shippable version, use a **zero-owned 0600 key file in Application Support**, created atomically under a 0700 private directory, with explicit disclosure that it is stored locally. Never copy it into payloads, git, logs, diagnostics or updates. A Keychain-backed store is an alternative only after noninteractive launchd access and ad-hoc update behavior are tested. Do not add an untested Keychain prompt to every scheduled run.

Store via a native secure field and narrowly scoped authenticated local endpoint, not a URL/query parameter or process argv. Clear any key cache after replacement. Display configured/tested status, never the full key. Test with a minimal synthetic request through `lib/jev.py`, with an explicit small usage warning, no email content and a bounded timeout. “Key present” and “Jev request succeeded” are different checks. User payment/access approval cannot be automated away.

### Drafting provider specification

Separate settings conceptually as `judgment_provider: jev`, `draft_provider: claude|codex|opencode|none`, and `draft_model`. Preserve existing explicit user selection during migration. Disable provider fallback unless the user explicitly enables it and can see the actual provider used. With no drafting provider, judgments, open loops, Gmail links and Undo remain available.

Add OpenCode as **one data entry** to `lib/llm.py`'s `KNOWN_PROVIDERS`, not a new dispatch branch:

```python
{
    "name": "opencode",
    "label": "OpenCode",
    "bin": "opencode",
    "bin_env": "OPENCODE_BIN",
    "wired": True,
    "argv_template": ["run", "--model", "{model}", "{prompt}"],
    "model_map": {},
}
```

The model must be the user's valid **`provider/model`** value, discovered from their configured OpenCode models and explicitly selected/tested. Do not forward the legacy `haiku` alias or invent an affordable/available model. `run` is the documented noninteractive interface. Confirm plain-text output of the supported version; `--format json` produces events requiring parsing and is not a drop-in replacement for `run_prompt`'s text contract. Distinguish current OpenCode from older unrelated/archived CLI implementations. [O1]

The data entry wires invocation, not operational safety. A separate generic drafting hardening item must run agents with stdin closed, bounded execution/output, an empty zero-owned working directory and a tested no-tools/no-MCP configuration where supported. A drafting agent must not execute instructions embedded in email, inspect unrelated local files, or get access to Gmail/Jev credentials just because it runs under the user's account. An empty directory alone is not a sandbox. Validate each provider's actual permission controls, using an explicitly selected text-only agent/profile if needed. If safe headless drafting cannot be established, disable that provider with a clear reason, not an interactive approval prompt hidden behind the menu bar.

## First-run doctor

Add **`zero doctor`**, available from the installed launcher, setup, Settings and the install failure output. It must work without the keeper server. The shell entry performs OS/tool/path checks even if Python is absent; the Python doctor supplies deeper checks when available. The GUI implements enough native startup diagnostics to show the same failures before Python starts. Share stable check IDs/results rather than maintaining three contradictory checklists.

Proposed interfaces, not existing commands:

- `zero doctor`: safe local inspection, no mailbox writes, no consent prompts, no package installation, no paid model requests.
- `zero doctor --online`: user-approved bounded Google profile/read and synthetic Jev checks; may refresh Google tokens and consume minimal Jev usage. State that explicitly.
- `zero doctor --draft`: optional chosen-CLI synthetic prompt, with cost/privacy notice. Never needed to validate sweeping.
- `zero doctor --json`: machine-readable schema with check ID, severity, observed value, fix text/action, timestamp and exit status. No credentials or email content.
- `zero doctor --context launchd`: same environment/path/key checks as a scheduled run, no real sweep.

Exit 0 means required checks for the requested mode passed, 1 means a blocking prerequisite failed, 2 means doctor itself could not complete. Warnings do not block. Unchecked online checks must print NOT TESTED, never PASS. Default offline success is not permission to claim “ready for a first sweep”.

| Check | Required? | Failure fix line |
| --- | --- | --- |
| OS, hardware, Rosetta, SDK when source install/update selected | Required for that install mode | `FIX: Use an Apple Silicon Mac with macOS 26+, and install a compatible Command Line Tools SDK. Open native Terminal if running under Rosetta.` |
| App path, version, bundle ID, signature, quarantine/translocation | Required | `FIX: Repair this release with the installer. Do not disable Gatekeeper. See the recorded launch/security error.` |
| Free space, destination/runtime/log permissions and private credential modes | Required | `FIX: Free space or choose a writable user Applications location. Restore access only to zero's named directory.` |
| Python version + actual imports | Required | `FIX: Install the documented compatible Python, then rerun doctor. Command Line Tools alone is not this check.` |
| gws executable, supported version and CLI flags | Required | `FIX: Install the release-pinned @googleworkspace/cli into the documented user prefix, or select a compatible gws binary.` |
| GUI and scheduled executable resolution | Required | `FIX: Select this executable's absolute path in Settings. A shell-only PATH entry is not visible to the app.` |
| Runtime payload, settings/account/policy schema | Required | `FIX: Restore the runtime through Repair install. Back up invalid user configuration and correct it; never silently reset it.` |
| Backend identity/version, loopback bind, auth handshake, conflicting listener | Required when app is running | `FIX: Restart zero, or use the reported free port. Do not terminate another application's listener.` |
| OAuth Desktop client validity/provenance/Google endpoints | Required | `FIX: Repair the bundled client resource or import your own Desktop client in Setup → Google.` |
| Per-account token availability, identity and requested capabilities | Required for selected accounts | `FIX: Reconnect <account> in Accounts and approve Gmail access. Existing cached data remains available.` |
| Google API/profile read, error-body parsing even if gws exits 0 | Online required before first sweep | `FIX: <Reconnect / enable API in your project / ask Workspace admin / shared-client limit: use BYO>, based on the returned error.` |
| Testing status / shared-client capacity | Advisory or UNKNOWN unless authoritative evidence exists | `FIX: Confirm In production in your project's Audience page and reconnect. For bundled-client capacity, consult maintainer status; local files cannot measure it.` |
| Jev key present, readable by app/CLI/launchd, not exposed | Required | `FIX: Enter your key in Setup → Judgment. Do not paste it into Terminal history or an issue.` |
| Jev synthetic auth/network/schema check | Online required before first sweep | `FIX: Replace key / check account usage / wait until retry time / retry service, matching the returned error.` |
| Drafting executable, model, login and safe headless profile | Optional | `FIX: Choose and sign into an installed Claude, Codex or OpenCode CLI, or continue without drafting.` |
| Notifications | Optional | `FIX: Allow zero in System Settings → Notifications if you want alerts. Failures remain visible in zero.` |
| Files & Folders / protected paths | Normally unnecessary | `FIX: Move zero runtime to Application Support. Approve access only for an explicitly selected external file. Full Disk Access is not a setup prerequisite.` |
| Accessibility, Screen Recording, Automation | Not required for normal zero workflow | `FIX: None. Do not request these permissions merely to run sweeping or the global hotkey.` |
| LaunchAgent enabled, absolute paths, key access, last result | Required only if scheduling enabled | `FIX: Re-enable the schedule from Settings, then run the launchd-context doctor. Inspect the named daily log if it still fails.` |
| Recovery journal/state writes and first-run mutation gate | Required | `FIX: Restore writable recovery storage before a sweep. No archive operation starts without recoverable bookkeeping.` |
| Network/clock/TLS to GitHub, Google, Jev | Required for the relevant online operation | `FIX: Correct the clock or connection/proxy. Never disable certificate checks.` |

Example output:

```text
PASS  runtime.python          /opt/homebrew/bin/python3 (supported)
PASS  google.personal.read    Profile and inbox read succeeded
FAIL  judgment.jev.auth       Jev rejected the supplied key
      FIX: Open zero → Setup → Judgment → Replace key, then Test connection.
WARN  drafting.provider       No drafting CLI selected. Sweeps do not require one.
PASS  permissions.disk        Full Disk Access is not required
NOT TESTED google.shared_cap  Not observable from this installation
RESULT: Not ready to sweep. 1 required check failed. No mail was changed.
```

Provide Copy diagnostics with an on-screen preview. Redact account addresses by default, auth URLs/codes, tokens, key files, request headers, subjects/bodies, draft text and arbitrary provider stderr. Keep a stable support code and relevant path/version. Never upload logs automatically.

## Error visibility contract

Every operation has `idle`, `running`, `succeeded`, `incomplete`, `failed`, and `cancelled` outcomes where applicable. A failure includes a stable code, phase, actionable message, retryability, fix action, timestamp and sanitized detail. Persist the last failure across panel dismissal and app restart. A transient toast may supplement it but cannot be its only surface.

- **Before native launch:** terminal summary + log path, nonzero exit, old app preserved.
- **Native app up, backend down:** native failure view, Retry/Open logs/doctor, no dependency on a backend endpoint to explain why the backend failed.
- **Backend up, setup incomplete:** blocking capability cards. No automatic sweep and no misleading empty-inbox view.
- **Mid-run:** per-account progress and safe cancellation. Failed classifications preserve mail, failed writes preserve truthful partial counts, unknown write outcomes reconcile with Gmail before retry.
- **Background/scheduled run:** durable warning badge and last-success age. Best-effort notification is additional, never required for visibility.
- **Recovery:** repeat only the failed safe stage. Do not erase a connected account because a new account's auth failed, cancel another tool's auth, reset all configuration, or send a draft to test connectivity.

## Updates without an Apple account

Keep the current **check automatically, install only on click** behavior. Ad-hoc signatures do not provide publisher authentication. No updater can honestly replace Apple's Developer ID trust with `xattr` or `codesign --verify` alone.

Current `Updater.swift` has useful six-hour checks and failure breadcrumbs, but:

- It observes one release and downloads moving `latest`, so the installed version may differ from the shown version.
- It does not validate download HTTP status, release asset identity/hash or staged signature before replacement.
- `rm -rf "$DEST" && mv "$STAGE" "$DEST"` is not an atomic replacement transaction. `mv` may be atomic, but deletion followed by a failed move leaves no app to reopen.
- The breadcrumb is next to the app, potentially unwritable. Quarantine errors are suppressed and helper relaunch has no health confirmation.
- A source install would become binary-installed on its first update.
- Application Support code is overwritten on launch; partial payload refresh or incompatible schema migration can break rollback even if an older app bundle survives.

Specify `install_mode`, installed release/commit and supported runtime schema in zero-owned metadata. Source installs update by fetching the selected immutable source release + client resource, compiling locally and using the same verified transactional installer. The update button says **Build and install update**, shows progress and keeps the old app running during compilation. If CLT is missing/broken, leave the old app usable and offer repair or an explicitly consented switch to binary mode. Binary installs use the corresponding release asset, never moving `latest` after selection.

Common update transaction:

1. Confirm release asset/commit, architecture, minimum OS, expected version and digest. Enforce HTTPS/known release origins and refuse downgrades unless deliberately requested. Respect GitHub rate limits and show “last check failed” with last successful check time rather than “up to date”.
2. Build/download into a unique private stage. Validate bundle/payload and ad-hoc signature before quit. No changes to accounts, keys, policy, drafts or the schedule at this stage.
3. Stop only zero-owned jobs/processes, wait for in-flight mutation bookkeeping to reach a safe point, then quit. Do not interrupt a Gmail mutation and report it as successful.
4. Rename the old bundle to a backup, move the verified stage into place, roll back if any step fails. Persist the transaction journal in writable Application Support. Use unique helper/stage paths, a lock and safe quoting. Check free space and target writability before asking the app to quit.
5. For binary mode only, apply the explicit scoped quarantine handling above and verify it. For source mode check that the locally built output did not inherit it. Never mutate unrelated extended attributes.
6. Relaunch and wait for app/backend version + schema health acknowledgement. Keep logs and a visible terminal/native recovery path if the new app cannot launch. Restore old bundle and compatible runtime snapshot on failure; if schema rollback cannot be guaranteed, block that update before install or ship a backwards-compatible migration.
7. On confirmed success, publish “Updated to X” and retain one bounded rollback version. Refresh code atomically/versionedly in Application Support while preserving user data. New client defaults must never overwrite an existing user's chosen client or credentials. A client migration requiring new consent is a separate visible action.

For stronger publisher authenticity without Apple membership, a future release-signing key and pinned public verifier can authenticate manifests. This is separate from ad-hoc macOS signing and requires key custody/rotation/recovery design. Same-origin SHA-256 checksums detect corruption but not a compromised GitHub publisher. State the trust level actually shipped.

## Prioritized, individually shippable work

Each row can ship behind existing behavior or a feature gate. Do not change the public default until its dependencies pass. File names below are proposed implementation targets, not permission for this planning task to edit them.

| Priority / item | What changes | Files | Verification before declaring it shipped |
| --- | --- | --- | --- |
| P0.1 Honest prerequisite and privacy docs | Correct production-vs-Testing contradiction, warn about cap and unverified warning, separate Jev/drafting, remove “nothing leaves your Mac”, state hardware/SDK and one-command limits. | `README.md`, `docs/SETUP.md`, `docs/GOOGLE_VERIFICATION.md`, `SECURITY.md`; later synchronize `landing/` privacy/setup copy. | Compare every install/privacy claim with actual release behavior and requested OAuth scopes. No proposed command advertised as working before it exists. |
| P0.2 Structured readiness and errors | Introduce stable capability/check schema, persistent failure state and per-account diagnostics. Parse gws JSON errors even with exit 0. No “all kept” success on failed judgment. | New `lib/doctor.py`, `lib/keeper_server.py`, `lib/review_open_loops.py`, `lib/dashboard_state.py`, tests under `lib/tests/`. | Inject missing deps, JSON/API errors, Jev timeout/schema failure, partial Gmail writes and state corruption. Assert no archive on failed classification and exact failure counts. |
| P0.3 CLI doctor independent of server | Add doctor dispatcher and shell-level fallback when Python/config is broken; no model/mail calls by default. | `bin/zero`, `config.sh`, new `lib/doctor.py`, shell/Python tests. | Empty PATH, no Python, broken config, no server, offline, JSON mode and exit codes. Assert no consent/package/network mutation occurs in default mode. |
| P0.4 Persistent native boot failure | Surface runtime seeding/spawn/port failures without relying on server. Keep existing first-run auto-open, reopen and shortcut. | `macapp/Sources/main.swift`, `KeeperModel.swift`, `KeeperAPI.swift`, `OnboardingView.swift`. | Fresh GUI login with no shell environment, unavailable Python, occupied port, hidden menu icon, multiple displays, crash before health. Must reach an actionable view or installer error within bounded time. |
| P0.5 Jev key onboarding and separation | Add secure entry, persistent key resolver shared with scheduled runs, synthetic test, Jev-only judgment readiness. Do not override an existing user's provider choice implicitly. | `lib/jev.py`, `lib/keeper_server.py`, `lib/llm.py`, `macapp/Sources/OnboardingView.swift`, `KeeperModel.swift`, settings view/model. | Missing/wrong/replaced key, cache invalidation, 401/403/429/5xx/bad schema, fresh Finder launch and launchd-context check. Inspect logs, payload and diagnostics for key leakage. |
| P0.6 Optional drafting and OpenCode data | Add the data entry above, draft provider/model setting, optional skip and no silent vendor fallback. Remove Claude as an installer/onboarding prerequisite. | `lib/llm.py`, `lib/keeper_server.py`, `lib/gen_drafts.py`, `KeeperModel.swift`, `OnboardingView.swift`, `macapp/install-zero.sh`. | No agents: first Jev sweep succeeds, Reply explains disabled state. Claude-only, Codex-only and OpenCode-only installations retain selected agent. Nonzero/timeout must not invoke another vendor. Fake argv tests plus real synthetic smoke tests on supported CLI versions. |
| P0.7 Draft subprocess safety | Safe text-only profiles, no tools/MCP, isolated working directory, closed stdin, bounded/redacted output. | `lib/llm.py`, draft call sites and tests. | Email prompt-injection fixture requesting shell/file/network actions cannot perform them. Unauthorized/auth-expired CLI exits with a fix, never a hidden prompt. This gates enabling each provider for real mail. |
| P0.8 Isolate and harden OAuth | Zero-owned client/account config roots, strict Desktop schema/Google endpoint validation, scoped process ownership, per-account reconnect and explicit cap/policy errors. Preserve existing credentials via a deliberate migration, not destructive moves. | `lib/keeper_server.py`, `lib/draftutil.py`, `config.py`, `OnboardingView.swift`, `KeeperModel.swift`. | Concurrent unrelated gws login survives cancel/retry. Import rejects Web/service-account/hostile endpoint JSON. Denied scope, disabled API, timeout, duplicate, cap fixture and admin block produce distinct actions. Existing account remains usable. |
| P0.9 Client-in-source-install bridge | Require same-release OAuth resource for consumer source builds; extract only installed-client JSON from official DMG and feed build override. Document public-client risk and BYO fallback. | `macapp/install-zero.sh`, `macapp/build.sh`, release workflow/scripts, `docs/GOOGLE_VERIFICATION.md`. | Clean machine with no maintainer config builds locally with bundled sign-in available. Missing/wrong/hash-mismatched resource blocks with repair. Payload scan finds client JSON but no user tokens/keys/accounts. Never executes downloaded app. |
| P0.10 Safe source installer | Source default behind flag first; immutable release resolution, SDK probe, prerequisite gates, user destination, staged replacement, launcher and launch handshake. Signing failure fatal. | `macapp/install-zero.sh`, `macapp/build.sh`, new installer tests/release manifest as needed. | Clean macOS 26 Apple Silicon install with no Homebrew/CLT, and one with tools preinstalled. Exercise declined permission, SDK mismatch, offline, disk full, interrupted copy/build, existing app. Rerun is non-destructive. |
| P0.11 First-sweep gate and receipt | Explicit user action after online checks, optional preview, separate backlog action, durable progress/results/Undo. | `lib/keeper_server.py`, `lib/review_open_loops.py`, `lib/dashboard_state.py`, `KeeperModel.swift`, `OnboardingView.swift`. | Dedicated test mailbox with known messages, no real user mail. Successful sweep counts match Gmail label state; Undo restores archived messages. Cancel/network interruption shows incomplete status and retry reconciles writes. |
| P0.12 Transactional mode-aware updater | Preserve source/binary mode, pin selected release, validate stage, rollback bundle/runtime, writable diagnostics and health receipt. | `macapp/Sources/Updater.swift`, `main.swift`, update model/manifest decoding, shared installer helper. | Source→source and binary→binary updates, permission denial, bad asset/signature, helper failure, kill between rename steps, bad new server, version mismatch, old data/schema. Old app remains recoverable and success never precedes health. |
| P1.1 Scheduled diagnostics | Same paths/key resolution and last-failure reporting as manual runs; no mandatory notifications. | `bin/zero`, `config.sh`, `lib/keeper_server.py`, `lib/notify_run.py`, `KeeperModel.swift`. | Logged-in launchd dry check with sparse environment, offline/sleep/resume, expired Google token, denied notification permission. Confirm no silent stale-success indicator. |
| P1.2 Release acceptance automation | Disposable-home tests, payload leak guard extensions, release source/client/version parity checks and real-Mac checklist. | `macapp/build.sh`, release workflow, `lib/tests/`, new `docs/RELEASE_CHECKLIST.md`. | Include `.env`, Jev key files, tokens and client type in leak checks. Test source and browser-downloaded DMG on fresh macOS 26/current supported patch. Save logs/screenshots and exact OS/tool versions. |
| P1.3 Cap operations and support | Maintainer audience/quota checks, pre-cap warning process, app error help, sanitized support bundle and public limitation statement. | `docs/GOOGLE_VERIFICATION.md`, `docs/SETUP.md`, doctor/UI help, release checklist. | Maintainer verifies actual console state/count. Simulated cap failure offers BYO immediately without repeated authorization or auto-project rotation. Never consume real user slots merely to test the cap. |
| P2.1 Verified scalable Google access | Decide verified desktop/hosted architecture, data processor obligations, verification/assessment and operating budget before broad acquisition or $4.99 promise. | New hosted/verification design doc, privacy docs and actual verification submission; implementation scoped separately. | Written current Google requirements + architecture review, successful verification and test authorization beyond unverified restrictions before claiming scale. Payment collection is not verification. |

**Release gate:** finish P0.1–P0.11 and demonstrate a clean first sweep before promoting the source command. Until P0.12 ships, disable the current binary-only in-app install action for source-mode users and offer a safe rerun of the pinned source installer. Keeping update availability checks is fine. Do not ship a source default that reintroduces the downloaded-app problem on its next update.

## Acceptance matrix and honest limits

Minimum end-to-end evidence, not just unit tests:

- A clean local macOS 26 Apple Silicon user with no maintainer files, CLT, Homebrew, Python, Node or agent CLI follows the release command. Interactive OS prerequisites are acknowledged. Setup appears, valid Jev/Google connect succeeds, a fixture mailbox sweep succeeds, drafting is clearly optional, and Undo works.
- Existing compatible tools are reused, including gws used by other software. zero neither replaces that software's credentials nor kills its login process. Run separately with Claude-only, Codex-only, OpenCode-only and no agent installed.
- Browser-downloaded DMG under normal quarantine on macOS 26/current supported patch, source-built app, managed-machine refusal, malformed signature, unavailable SDK and denied writes all have truthful, visible outcomes. A managed refusal need not succeed to pass the error-handling test.
- OAuth normal warning/proceed, no Advanced link, cap fixture, revoked client/token, wrong account, denied scope, API disabled and Testing→production reconnect are covered. A day-8 Testing test is a scheduled integration test or controlled expiry fixture, not a claim based on a short session.
- Source/binary updates each preserve install mode, data, keys, policy and client choice. Deliberately interrupt replacement and fail new-version health checks to prove rollback.
- No secrets/content in diagnostic export. No mailbox mutations before user Run/confirmed preview apply, no draft sending from diagnostics, no hidden provider switch, no requirement for Full Disk Access or Accessibility.

This planning pass did **not** run an installer, compile zero, authorize Google, consume a Jev key, change any cloud setting, mutate mail, or validate Gatekeeper on a clean macOS 26 machine. The matrix above is work still required, not evidence already obtained.

What cannot be foolproof:

1. **Unlimited strangers plus a 100-user lifetime shared cap.** Verification or user-owned clients are the only honest product paths here. An installer cannot fix it.
2. **One command with no human setup.** Google consent, Jev account/key acquisition, first-use CLI login and some Apple/admin prompts require user action.
3. **Guaranteed unnotarized execution everywhere.** Source builds avoid the normal quarantine problem; device policy, malware protection and future OS changes still win.
4. **Automatic trust.** Source availability, an ad-hoc signature, a checksum and Google's warning bypass are not security certification.
5. **Always-on behavior on a sleeping/offline local Mac.** Say when work last succeeded and what remains pending.
6. **Perfect AI judgment or perfect network transactions.** Keep uncertainty safe, make errors visible, journal writes and make archive reversible. Do not market typed responses as eliminating service/schema failures.
7. **An assessed/verified hosted Gmail service for a presumed fixed low cost.** Verify requirements and unit economics before promising the tier.

## Sources and evidence notes

External policy/docs reviewed through a read-only research task on 2026-09-17. URLs are included so policy-sensitive decisions can be rechecked at implementation/release time. Where a page has no displayed date, access date is not a claim of publication date. No authoritative source reviewed establishes that `xattr` guarantees Gatekeeper acceptance on macOS 26+.

- **[A1] Apple, Safely open apps on your Mac** (page dated 2026-05-27): https://support.apple.com/en-us/102445 . Developer ID/notarization checks and Privacy & Security → Open Anyway. This supports the documented override, not blanket attribute-stripping advice.
- **[A2] Apple, Open a Mac app from an unknown developer** (macOS Tahoe 26 guide): https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac . Version-specific unknown-developer handling. Also Developer ID distribution overview: https://developer.apple.com/developer-id/ .
- **[G1] Google, Unverified apps:** https://support.google.com/cloud/answer/7454865 . Documents warnings and “100 new users in total”. Google OAuth verification FAQ: https://support.google.com/cloud/answer/9110914 .
- **[G2] Google, OAuth 2.0, refresh token expiration:** https://developers.google.com/identity/protocols/oauth2#expiration . External Testing seven-day expiry and other refresh-token invalidation conditions. The identity-only exception does not apply to `gmail.modify`.
- **[G3] Google, OAuth 2.0 for iOS & Desktop Apps** (page reported updated 2026-08-07): https://developers.google.com/identity/protocols/oauth2/native-app . Installed apps are distributed to devices and assumed unable to keep secrets; review PKCE/loopback requirements against pinned gws.
- **[G4] IETF RFC 8252, OAuth 2.0 for Native Apps** (October 2017), especially section 8.5: https://www.rfc-editor.org/rfc/rfc8252#section-8.5 . A shared embedded secret cannot prove a native client's identity. Protocol basis, not a Google contract exception.
- **[G5] Google APIs Terms of Service:** https://developers.google.com/terms . Credential-handling and suspension/termination obligations. Read together with installed-client documentation, not as proof that public git publication is expressly authorized.
- **[G6] Google, OAuth 2.0 best practices:** https://developers.google.com/identity/protocols/oauth2/resources/best-practices . Protection of OAuth credentials and tokens. Technical public-client status does not erase all credential-handling obligations.
- **[G7] Google, Restricted scope verification:** https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification . Google API Services User Data Policy: https://developers.google.com/terms/api-services-user-data-policy . Gmail scope classification: https://developers.google.com/workspace/gmail/api/auth/scopes . Verify assessment applicability and external AI processing with Google before making legal/compliance promises.
- **[O1] OpenCode CLI:** https://opencode.ai/docs/cli/ . Noninteractive `run`, `--model provider/model`, model discovery and output mode. Permissions reference: https://opencode.ai/docs/permissions/ . Exact safe headless profile and supported CLI versions remain release acceptance work.
