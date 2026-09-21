# Landing redesign verification

Date: 21 September 2026. Site artifact: `14e9e2b`.

## Scope and decisions

Replaced the old landing with one product explanation, approved anonymized app image, one installation path, setup requirements and native FAQs. Removed the hosted offer, fabricated inbox interactions and unsupported cost claims. Kept the existing static nginx deployment. Current product facts are grounded in `README.md`, `macapp/install-zero.sh` and the app's settings. `PRODUCT.md` contains older aspirations and was not treated as release documentation.

The visual direction follows the user's charcoal/warm-red and Raycast-restraint reference, without copying Raycast. See `landing/DESIGN.md`. The app's native blue and fictional screenshot content remain unchanged.

## Evidence

| Requirement | Observed result |
| --- | --- |
| Understandable copy | 1,633 words reduced to 591. Rival-family Claude cleanse followed by SlopMonster 5/5 CLEAN. |
| Desktop and narrow layouts | Browser checks at 1440×900, 390×844 and 320×844 found no horizontal overflow. Initial responsive checks used same-origin iframes because direct resizing was unavailable. |
| Main interactions | Install anchors, clipboard success feedback, native setup/FAQ disclosures and visible keyboard focus passed in the browser. |
| Clipboard recovery | `node --test landing/test-site.mjs`: 4/4 passed, including denial/retry, pending and unavailable API states. These supplement, not replace, browser checks. |
| Readability | Browser-reported text/CTA contrast ranged from 9.29:1 to 16.48:1. Local Geist fonts and the 1349×1166 app artwork loaded. |
| Packaging | `PORT=8100 bash landing/build.sh zero-landing:14e9e2b` passed all 11 route checks, including CSS, JS, fonts, image, legal pages, both redirects and unknown-path 404. |
| Installer | Redirect returned a 280-line bash script and passed `bash -n`. Public installer SHA-256 matched the repository file. Installer was not executed. |
| Installation consent | Independent finish reviewer requested a visible warning before the command. Added notarization status, possible Homebrew/tool installation and Google's warning. Final desktop/mobile recaptures confirmed order and legibility. |
| Design finish | Final reviewer disposition **PASS**. Installation trust finding **RESOLVED**, no remaining material issues in the requested verification. Detector's only findings were retained Geist/Geist Mono font-choice warnings. |
| Source delivery | Implementation and follow-up committed and pushed to `master`: `40e86c3`, `14e9e2b`. |

## Deployment handoff

### Additional end-user acceptance on the release image

The final image was run through its real nginx interface at `http://127.0.0.1:8101/`, without the Python preview server or test fixtures. A browser visitor followed the install action, observed the TypeSafe billing and external-email-processing disclosures, read the warning before the command, and clicked Copy. The real UI announced “Copied. Paste it into Terminal when you’re ready.” Clipboard contents were not independently pasted during this run.

The visitor followed the script-review link through nginx to `https://github.com/drewling/zero/blob/master/macapp/install-zero.sh`, opened both rendered legal pages, and opened the recovery FAQ to find the Undo instructions. No installer execution or mailbox authorization was attempted because this is website acceptance, not an app installation request.

An independent worker launched a separate disposable instance, checked all asset and redirect boundaries, and confirmed served homepage bytes exactly match `git show 14e9e2b:landing/index.html`. The candidate contains no hosted offer and places the disclosure before the command.

The improvement is observable in this acceptance path: the visitor can find the actual requirements and costs, inspect the real script, copy the installation command, and find recovery guidance without navigating staged demos or a competing hosted offer. Copy volume fell by about 64%. This is evidence of a simpler working path, not a claim of measured conversion lift or a human usability study.

A fresh public fetch still returned the old title, “zero — an inbox you can finally ignore,” and the `$12` offer, without the new headline. This confirms that source publication did not deploy the website. Live delivery remains blocked as described below.

**Not deployed.** Production remains unchanged. GCP authentication for the existing account expired and requires interactive `gcloud auth login`. This was checked again after visual verification. Native Dokploy schema discovery returned no callable tools in this session, so no alternate production mutation was attempted.

The local Docker image `zero-landing:14e9e2b` is smoke-tested. A complete deployment archive is prepared in the coordinator's scratch directory as `zero-landing-14e9e2b.tgz`. Build again on the server for its architecture rather than transferring the Mac-built image.

After reauthentication, follow `docs/MAINTENANCE.md`: inspect the current Zero compose service and stored Dokploy compose, retain both backups, build and smoke-test the new image, change only `zero-landing`, then verify the public homepage, assets and installer. Do not restart unrelated services or use the generic `landing/deploy.sh` defaults.
