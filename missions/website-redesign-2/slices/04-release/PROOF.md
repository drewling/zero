# Release proof: website redesign 2

**Released by:** advisor-lead@kernel on 2026-09-29 at 15:25Z. **Owner approval:** Tayo, 15:13Z ("Zero redesign - get it live"). He kept all 3 provisional choices: manual **Run zero now** with no automatic schedule promise, "Only the mail that still needs you.", and "Check it with your coffee. Then close it."

## What shipped

- Reviewed candidate `3f8f1a4`. The `landing/` tree is identical at pushed master `530da54` (tree `482e7b7c`).
- `master` was pushed to `origin` (`5728395..530da54`). A secret scan of the pushed range found nothing.

## How it was deployed

- gcloud needed an interactive re-login, so SSH to `production-server` wasn't available. Instead, Dokploy raw Compose `u2SP2b5035tm1yaHVNcH8` was changed from the local image `zero-landing:0505816` to a build pinned to the exact public commit:
  `build.context: https://github.com/drewling/zero.git#530da54…:landing`, `image: zero-landing:3f8f1a4`, `pull_policy: build`.
- Only `zero-landing` changed. The Compose API read-back matched the new file. The deployment status is `done`.
- The previous Compose was saved to `~/.jcode/scratch/zero-r2/compose-before-1790695515.json`.

## Live checks (https://zero.headless.com)

- These files matched the candidate byte for byte (SHA-256): `index.html`, `site.css`, `site.js`, `privacy.html`, `terms.html`, `robots.txt`, `llms.txt`.
- Every file under `landing/assets` returned 200.
- `/install` returns 302 to the raw GitHub installer and `/install.sh` returns 302 to the GitHub script view. An unknown path returns 404. The fetched installer passes `bash -n` (it was not run).
- Live Chromium (Playwright) at 1440, 390 and 320:
  - The h1 reads "Only the mail that still needs you."
  - No horizontal overflow, no broken images, no console errors and no 4xx or 5xx responses.
  - The copy button shows "Copied. Paste it into Terminal when you're ready." and changes to "Copy again".
  - Screenshots: [1440](proof/live-chromium-1440.png), [390](proof/live-chromium-390.png).
- Not checked live: WebKit (the local browser isn't installed), VoiceOver, axe and performance scores.

## Rollback

Restore the `composeFile` from the saved JSON (image `zero-landing:0505816`, which still exists on the server) with `compose.update`, then run `compose.deploy`. The helper script is `~/.jcode/scratch/zero_dokploy.py`.
