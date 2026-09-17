# Distribution research brief

*Research-only. Sources accessed 2026-09-17. This report is decision-ready and marks unsupported Tahoe or policy specifics as unverified.*

## 1. macOS distribution

**Do not position Homebrew as a Gatekeeper bypass.** Current Homebrew Cask source explicitly applies a web-download quarantine record and propagates it into installed artifacts: [Homebrew macOS quarantine implementation](https://github.com/Homebrew/brew/blob/main/Library/Homebrew/extend/os/mac/cask/quarantine.rb) (accessed 2026-09-17). `depends_on` only declares OS/architecture dependencies, and there is no cask-level `quarantine: false` solution that makes an unnotarized app trusted.

Apple’s supported path for an app that is unnotarized or from an unidentified developer remains: attempt launch, then **System Settings → Privacy & Security → Open Anyway**, confirm, and macOS saves an exception for future launches: [Apple, Safely open apps on your Mac](https://support.apple.com/en-us/102445) (accessed 2026-09-17). This is the least-friction **supported** no-notarization path.

`xattr -dr com.apple.quarantine Zero.app` is still a real mechanism. Current Homebrew itself removes the same attribute with `xattr -d` when explicitly releasing quarantine: [Homebrew quarantine source](https://github.com/Homebrew/brew/blob/main/Library/Homebrew/cask/quarantine.rb) (accessed 2026-09-17). But **its practical success against Tahoe Gatekeeper for this exact ad-hoc-signed release is unverified** without a clean Tahoe test. Likewise, Apple’s current Tahoe-era support article does not document Finder’s right-click → Open path. A current OSS comparable still instructs users to use it ([FlowDictate](https://github.com/Hank1210/FlowDictate), accessed 2026-09-17), but that is not Tahoe-specific proof.

**Recommendation:** ship a signed ad-hoc ZIP via `curl | bash` only if the installer verifies a published SHA-256, installs to a user-owned location, and presents the documented **Open Anyway** steps. Optionally offer an explicitly explained `xattr -dr` convenience path, but do not promise it will bypass Tahoe universally. Test the release ZIP on a clean Tahoe system before publishing either claim.

There is no free notarization route for a normal independent developer. Apple says Developer Program membership costs **US$99/year** and requires completing membership purchase: [Apple Developer Program enrollment](https://developer.apple.com/programs/enroll/) (accessed 2026-09-17). A free Apple Account is insufficient. Fee waivers exist only for qualifying nonprofit, accredited education, or government entities.

## 2. Google OAuth

The bundled production-unverified restricted-scope client is a hard product cap. Google says an unverified app is **limited to 100 new users until verified**, and describes this as a total limit rather than a daily quota: [Google Cloud, Unverified apps](https://support.google.com/cloud/answer/7454865) (accessed 2026-09-17). The official page does **not** specify the literal user-101 error or UI. Treat user 101 as unable to complete new authorization until verification, rather than promising a particular error string. Existing-user continuity at that point is also not explicitly guaranteed on that page.

For an OSS Gmail client, the realistic choices are:

1. **BYO Google Cloud project and Desktop OAuth client. Recommended for unlimited community distribution.** Each user bears their own 100-user project cap, which is irrelevant for personal use. Google’s documented prerequisites are: create/select a project, enable Gmail API, configure consent screen, create a Desktop client, and provide credentials: [Google OAuth 2.0 for iOS & Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app) (accessed 2026-09-17). In practice, expect roughly **6–8 Console actions**, plus paste/import into zero and browser consent. Deep links can open Console sections, but **a supported public API for fully scripting consumer OAuth-consent/client creation was not verified**.

2. **Ship the bundled client.** Best first-run UX, but fixed shared 100-new-user ceiling and unverified-warning friction. It is suitable only for a deliberately small trusted cohort.

3. **Verify restricted Gmail access.** This removes the cap/warning but triggers restricted-scope verification and, where Google’s criteria apply, periodic third-party security assessment: [Google, restricted-scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification) (accessed 2026-09-17). It conflicts with the owner’s stated cost constraint.

Publishing a Desktop client secret in an open-source app is not a meaningful secret exposure. Google’s own installed-app documentation says installed apps are assumed unable to keep secrets: [Google installed-app OAuth guide](https://developers.google.com/identity/protocols/oauth2/native-app) (accessed 2026-09-17). Still, document it as an identifier, not a credential that authorizes access by itself.

## 3. Jev / TypeSafe

TypeSafe’s current public site lists **Jev input cost as $42 per billion input tokens**: [TypeSafe AI homepage](https://typesafe.ai/) (accessed 2026-09-17). Its Quick Start says to log in to the console and obtain a key from the dashboard: [TypeSafe Quick Start](https://docs.typesafe.ai/introduction/quickstart) (accessed 2026-09-17).

**Unverified:** stranger self-serve entitlement, waitlist behavior, output-token pricing, free tier, and rate limits. The homepage exposes “Join Waitlist,” while docs direct login. Treat Jev as potentially gated and do not make it the sole BYOK provider until a fresh account can obtain a key.

## 4. Local coding-agent CLI providers

All three are usable from a launchd job **after initial authentication**, with absolute executable paths and an explicit `PATH`/`HOME`. launchd provides neither shell-profile PATH nor an interactive TTY.

- **Claude Code:** `claude -p --model <model> "prompt"` (`-p` queries then exits). [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference) (accessed 2026-09-17). `claude setup-token` creates a long-lived CI/script token for subscribers. Exact persisted-auth location is **not verified** from the primary docs.
- **Codex:** `codex exec --model <model> "prompt"` or `-m`; `--json` for machine output. [Codex command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-exec) and [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode) (accessed 2026-09-17). It reuses saved CLI auth, or accepts invocation-scoped `CODEX_API_KEY`.
- **OpenCode:** `opencode run --model provider/model "prompt"` or `-m`. [OpenCode CLI docs](https://opencode.ai/docs/cli/) (accessed 2026-09-17). Auth is stored in `~/.local/share/opencode/auth.json`, with environment and project `.env` alternatives.

## 5. Comparable OSS onboarding

No credible comparable found using a production `curl | bash` installer. The pattern is release ZIP or source build, then explicit permissions and a Settings key screen:

- [AIHelper](https://github.com/hendricius/aihelper) (accessed 2026-09-17): notarized release ZIP → drag to Applications → **Settings → API** → paste OpenAI key.
- [Spectr](https://github.com/henryoween/spectr) (accessed 2026-09-17): source build → Screen Recording permission → **Settings → AI** → paste OpenAI/Anthropic key → create workflow.
- [FlowDictate](https://github.com/Hank1210/FlowDictate) (accessed 2026-09-17): ad-hoc community ZIP → manual first-launch approval → onboarding chooses local or OpenAI mode, stores key in Keychain, then requests permissions.

## Product call

Use BYO OAuth client as the public Gmail path. Keep bundled OAuth only as an opt-in limited beta. Use documented **Open Anyway** as the supported unsigned-install fallback. Preserve non-Jev providers because TypeSafe access and free-tier status are not yet proven.
