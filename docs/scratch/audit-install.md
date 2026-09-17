# zero install / first-run audit

**Scope:** read-only audit of the requested installer, build, runtime, onboarding, provider, and identifier paths for a new user on a non-author Mac. No app/source files were changed. Findings below are based on code and docs inspected in the checkout. Where the published release artifact could not be inspected, that is called out explicitly.

## Prioritized issues

### 1. The one-line installer can fail for ordinary users installing to `/Applications`

- **Evidence:** `macapp/install-zero.sh:27` sets `DEST="/Applications/zero.app"`; `:133-135` removes any existing app and runs `cp -R "$APP_SRC" "$DEST"` without `sudo` or an authorization prompt.
- **User impact:** A standard user without write permission to `/Applications` gets `couldn't copy to /Applications (permissions?)`. The advertised curl command does not complete.
- **Smallest fix:** Install to `~/Applications` by default, or use a deliberate privileged copy step with a clear macOS password prompt.

### 2. The curl installer is not reliably unattended

- **Evidence:** `macapp/install-zero.sh:23` intentionally omits `-e`; `:59-65` runs Homebrew’s installer through `/dev/tty`; `:68-101` only warns when Homebrew, Python, Node, `gws`, or Claude installation fails.
- **User impact:** A piped invocation without an attached TTY can fail during Homebrew/Xcode setup, then continue into an install with missing dependencies. The user may see “Done” even though the app cannot function.
- **Smallest fix:** Detect an unavailable TTY and stop with a precise prerequisite message, or provide a tested noninteractive prerequisite path. Make prerequisite failures fatal before claiming success.

### 3. Platform support is narrower than the installer communicates

- **Evidence:** `macapp/build.sh:21-25` compiles only `arm64-apple-macosx26.0`; `macapp/install-zero.sh:41-42` merely warns when macOS is below 26 or the machine is not arm64.
- **User impact:** Intel users and users below macOS 26 can download and install an app that is expected not to launch. The installer does not stop or provide an alternative.
- **Smallest fix:** Fail early with explicit requirements, or ship a universal binary and a lower deployment target if supported.

### 4. First-run Google setup still requires a user-created OAuth client unless the release was built with one

- **Evidence:** `lib/keeper_server.py:1218-1234` creates a pending account and only reuses an existing client secret; `:1248-1267` launches `gws auth login` with the exact scopes. If credentials are absent, `:1333-1363` tells the user to create a Google Cloud Desktop OAuth client. In-app paste/save support exists at `:1453-1515` and is exposed at `:1971-1982` as `/api/set-credentials`.
- **Build evidence:** `macapp/build.sh:64-79` bundles `client_secret.json` only when `ZERO_CLIENT_SECRET` or `~/.config/zero-build/client_secret.json` exists. **The published release’s actual payload was not verified from this checkout.**
- **User impact:** If the release was built without that external file, a new user hits a substantial Google Cloud setup wall before connecting an account.
- **Smallest fix:** Make release builds fail if the intended bundled client is absent, or clearly advertise the manual Google Cloud setup before download.

### 5. BYO AI-key setup is not completed by onboarding

- **Evidence:** `lib/jev.py:20-23,57-71` reads the Jev key from environment variable `JEV` or a root `.env`; `macapp/build.sh:45-62` does not copy `.env` into the payload. `lib/keeper_server.py:1547-1551` defaults the provider to Claude. `lib/llm.py:239-283` falls back to Claude and returns `(\"\", False)` when execution fails.
- **User impact:** A user with only a Jev/API key has no in-app field or documented packaged-app location to enter it. A missing or unauthenticated Claude CLI can leave the first triage without a usable AI provider.
- **Smallest fix:** Add provider/key onboarding and persist it in Application Support, or prevent automatic triage until a usable provider is configured.

### 6. Onboarding presents Claude as mandatory even when another provider is intended

- **Evidence:** `macapp/Sources/KeeperModel.swift:66-70` defines `allGood` as Python + `gws` + Claude; `:158-175` preflights all three. `macapp/Sources/OnboardingView.swift:53-60` tells the user to install Claude when missing.
- **User impact:** A user intending to use Jev, Codex, or Hermes still sees a Claude prerequisite warning. The account connect button itself only requires `gws` (`OnboardingView.swift:75-86`), so the requirements are inconsistent.
- **Smallest fix:** Require Python and `gws` for Google onboarding, then validate the selected AI provider separately.

### 7. Source/CLI installation is manual and assumes account configuration

- **Evidence:** `install.sh:42-45,75-90` creates `accounts.json` from the example and tells the user to edit real `config_dir` paths. `setup.sh:65-72,95-100` likewise requires manual accounts and separate `gws auth login`. `accounts.json.example:2-4` contains literal `/Users/you/...` paths.
- **User impact:** A new CLI/source user must understand gws account directories and manually authenticate each account before `zero run` works.
- **Smallest fix:** Generate paths from `$HOME`, or make CLI setup use the same browser-based account onboarding as the app.

### 8. `run.sh` contains a nonportable Python path

- **Evidence:** `run.sh:14` sets a fixed PATH, while `:35` and `:51` invoke `/opt/homebrew/bin/python3` directly. `config.sh:17-21` already has a portable Python resolver, but `run.sh` bypasses it.
- **User impact:** Machines where Python is installed elsewhere, including `/usr/local` or a Python.org/conda install, fail in the scheduled/legacy runner even when `python3` is available.
- **Smallest fix:** Replace both absolute invocations with `$MAIL_TRIAGE_PYTHON`.

### 9. Launchd identifiers and docs remain Drewl-specific

- **Evidence:** `bin/zero:104-105,133,165-166` uses `com.drewl.zero.daily`; `lib/keeper_server.py:1555-1556,1596` uses the same label and path; `docs/SETUP.md:224-229` tells users to run `launchctl list | grep drewl`.
- **User impact:** This is not necessarily a first-run failure, but it is confusing for non-author users and can collide with an older Drewl installation.
- **Smallest fix:** Use one neutral reverse-DNS label and update all docs and migration logic.

## Runtime packaging verification

The distributed app **does carry the Python engine**. `macapp/build.sh:45-62` copies the allowlisted `lib`, `bin`, Python/config files, policy, categories, account example, and profile example into `Contents/Resources/payload`. `macapp/Sources/main.swift:99-140` copies that payload into `~/Library/Application Support/zero` and runs from there. The git checkout is not required at runtime.

User data is intentionally not bundled: `accounts.json` is not copied, and `main.swift:137` seeds only policy/categories if missing. Runtime state, accounts, drafts, logs, and learning live in Application Support. The packaged payload does not include `.env`, so Jev configuration is not automatically carried into a distributed app.

## Onboarding behavior confirmed

- **No accounts yet:** handled. `keeper_server.py:226-233` returns an empty list; `:1875-1877` returns a `needs_build`/empty-state sentinel; `KeeperModel.swift:148-155` shows onboarding only after the server is ready and accounts are empty.
- **OAuth failure:** handled with cancellation and a 180-second timeout at `keeper_server.py:1298-1325`, plus a generic retry message at `:1364-1368`.
- **Gmail API disabled:** handled with a recovery message and enable URL at `:1381-1390`.
- **Consent screen unavailable:** handled with an External/In production/test-user explanation at `:1391-1400`.
- **No AI provider:** detected in `/api/provider-status` at `keeper_server.py:1891-1898`, but not made a hard onboarding gate. `llm.py:254-283` ultimately falls back to Claude and can return failure.

## Personal identifiers and external assumptions

Whole-repo search found owner-specific references including:

- Repository/release URLs: `macapp/install-zero.sh:17,25`, `bin/release:82,115`, `macapp/Sources/Updater.swift:14`.
- Bundle identifier: `macapp/Info.plist:12` (`com.drewl.zero`).
- Personal contact: `SECURITY.md:13-16`, `landing/privacy.html:132`, `landing/terms.html:90`.
- Drewl project IDs, organization, and test users: `docs/GOOGLE_VERIFICATION.md:14-26`.
- Legacy Drewl launchd template: `deploy/com.drewl.mailtriage.plist.template:6`.
- Generic but misleading absolute examples: `accounts.json.example:2-4`.

These are mostly branding or documentation issues rather than confirmed runtime failures, but they should be generalized for a genuinely independent open-source distribution.

## External dependencies the installer does or does not handle

- macOS 26+, Apple Silicon: checked only as warnings by `install-zero.sh:37-42`.
- Homebrew: attempted by `install-zero.sh:57-65`; may require Xcode Command Line Tools and sudo.
- Python 3 and Node.js: attempted through Homebrew at `:98-100`.
- `gws`: attempted through npm at `:100`; still requires Google OAuth configuration and browser login.
- Claude CLI: attempted through npm at `:101`; still requires its own account/login/API access.
- Swift compiler, `iconutil`, and `codesign`: required by source builds in `macapp/build.sh:21-35,123-124`; not installed by the curl installer.
- Google Cloud project, Gmail API, OAuth consent screen, Desktop client, browser, and network: required by the first account flow; only the browser flow and recovery messages are automated.
- Jev API key: optional/provider-specific, but not collected by onboarding and not included in the packaged payload.
- `jq`: optional only, checked by `setup.sh:52-56` and not needed for the main app.
