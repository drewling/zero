# Release proof: slice 05 panel redraw

**Released by:** advisor-lead@kernel on 2026-09-29 at 16:48Z. **Owner approval:** Tayo at 16:40Z ("you can get the zero thing live"). The request came in at 15:35Z: re-create the app panel in the style of the rest of the site.

- **Candidate:** `c32f10d`, which passed review-qa at 16:45Z. The `landing/` tree is identical at pushed master `079971a`.
- **Deploy:** Dokploy raw Compose `u2SP2b5035tm1yaHVNcH8`, building `https://github.com/drewling/zero.git#079971a…:landing` as `zero-landing:c32f10d`. Only zero-landing changed, and the read-back matched. The container on production-server is healthy.
- **Live checks:**
  - `index.html`, `site.css`, `site.js`, `privacy.html` and `terms.html` match `c32f10d` byte for byte.
  - `/install` and `/install.sh` return 302, and the installer passes `bash -n`.
  - `/assets/panel-cut.png` returns 404 (removed). `/assets/zero-panel.png` returns 200 (it is the og:image).
  - Live Chromium at 1440, 390 and 320 showed no overflow, no broken images, no console errors and no 4xx or 5xx responses, and the copy button worked. Screenshots: [1440](proof/shots/live-1440.png), [390](proof/shots/live-390.png).
- **Not checked:** VoiceOver, Safari proper, Firefox and axe.
- **Rollback:** restore the Compose from `~/.jcode/scratch/zero-r2/compose-before-1790700499.json` (image `zero-landing:3f8f1a4`, still on the host), then run `compose.deploy` using `~/.jcode/scratch/zero_dokploy.py`.
