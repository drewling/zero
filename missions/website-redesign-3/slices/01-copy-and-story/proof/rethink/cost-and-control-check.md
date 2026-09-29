# Provider cost and control details checked for the rethink

Read-only checks 2026-09-29 22:55–22:56Z. These address specific reader questions, not a new service integration or account action.

## Authoritative cost route

- <https://docs.typesafe.ai/models> (Markdown source <https://docs.typesafe.ai/models.md>) advertises Jev 1.13 at **$42/billion or $0.042/million input tokens**, output tokens free. It says `jev-latest` currently resolves to `jev-1.13.0` and can change with future releases.
- <https://typesafe.ai/> independently displays the same provider's **$42 per billion input tokens**. This corroborates the provider documentation, but is not a second independent pricing authority.
- `lib/jev.py:34` selects `jev-latest`. Do not turn a current model-token rate into a guaranteed monthly inbox price, free allowance or future-rate promise. A verified **TypeSafe pricing** link to `https://docs.typesafe.ai/models` is a useful concrete addition without hardcoding a fragile rate into the 550-word page.
- Guessed `https://typesafe.ai/pricing` returned 404. Do not use it. A websearch attempt hit an anti-bot challenge; authoritative public documentation fetches succeeded without browser/account access.

## Recovery UI

`macapp/Sources/PanelView.swift:1053–1083` displays the day's readable batch and the actual **Restore all** control. `:1151–1175` displays readable sender/subject rows, an individual tray-up icon and tooltip **Put this email back in the inbox**. Do not invent a literal individual **Restore** label as a screenshot of the shipped UI. A labelled editorial explanation may identify the icon's effect, but must remain visibly editorial.

The dated Gmail recovery label is not a Finder folder containing a native Finder Restore control. Approved hero B uses a folder as a Macintosh editorial metaphor. Follow-on safety proof should identify zero's **Undo** tab as the place with restore controls. Gmail's **All Mail** provides searchability, not a substitute restore-button claim.

## Preview and reply-history explanation

`lib/review_open_loops.py:640,691` trims the classification preview to **160 characters**. `:974–998` sends `last_from_owner` and `replied_before` booleans (whether the owner sent the latest message and whether they have written to the sender), policy and conditional learned preferences. If the compact data row replaces vague “reply-history signals” with those plain meanings, preserve both fields. Do not claim all body content stays on-device, since the optional draft path sends more context.

## Conditional footprint

`macapp/install-zero.sh:94–112,114–156` respects existing tools. It may add Homebrew, Python, Node and the Google Workspace CLI. Claude Code is added when none of the supported coding tools is found. Reader claims that all five always install “silently” overstate the source. Name the conditional footprint plainly and put it before the command. Non-notarized does not mean unsigned: build uses ad-hoc signing (`macapp/build.sh:122–127`).
