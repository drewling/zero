# Maintenance checklist

This doc tells future Claude Code sessions (and human maintainers) what to keep
in sync, and how to release. Follow it every time you ship a change.

---

## When you change the API (endpoints, bodies, responses)

1. Update `docs/api/openapi.json` to match — add/remove paths, tweak schemas, fix
   descriptions. Run `python3 -m json.tool docs/api/openapi.json >/dev/null && echo OK`
   to confirm valid JSON.
2. If the change is user-visible, add a sentence to the relevant README section.

## When you change settings (`_DEFAULT_SETTINGS` in `keeper_server.py`)

1. Add / remove / update the key in the `Settings` and `SettingsUpdate` schemas in
   `docs/api/openapi.json`.
2. Update the settings table in `README.md` (if there is one there) and any prose
   in `docs/SETUP.md` that mentions that key.

## When you change `lib/llm.py` (providers, model map)

1. Update `docs/api/openapi.json` — the `provider` enum in `Settings` and the
   example in `GET /api/provider-status`.
2. Update the providers table in `docs/ARCHITECTURE.md` if the set changes.

## When you change the release process (`bin/release`)

Update the **Release process** section below and the matching section in
`CONTRIBUTING.md`.

## When you change the app significantly (new tab, renamed feature, UI flow)

Update `README.md` (feature list, panel table, screenshots) and
`docs/ARCHITECTURE.md` (request flow section if new endpoints are involved).

---

## Before every release

In order:

1. **Bump the version** — update `CFBundleShortVersionString` in
   `macapp/Sources/zero-Info.plist` (or wherever the Swift bundle version lives).
2. **Add CHANGELOG section** — add `## [X.Y.Z] - YYYY-MM-DD` to `CHANGELOG.md`,
   moving items out of `## [Unreleased]` into the new section. Keep a Changelog
   1.1.0 format.
3. **Verify docs are in sync** — run through the checklists above for anything
   changed in this release.
4. **Commit and push `master`** — the release script requires a clean tree on
   master. Push master separately before running `bin/release` (the script only
   pushes the tag, not the branch).

   ```bash
   git push origin master
   ```

5. **Run the release script:**

   ```bash
   bin/release X.Y.Z
   ```

   The script:
   - Verifies you are on `master` with a clean working tree.
   - Verifies `CHANGELOG.md` has a `## [X.Y.Z]` section.
   - Builds `zero.app` via `macapp/build.sh`.
   - Packages `zero.dmg` via `macapp/make-dmg.sh`.
   - Computes `zero.dmg.sha256`.
   - Creates and pushes the git tag `vX.Y.Z`.
   - Publishes a GitHub release (`gh release create`) with the changelog notes and
     the `.dmg` **and its `.sha256`** attached.
   - Installs `zero.app` to `/Applications/zero.app` and relaunches it.

   Requirements: Xcode CLT, `gh` CLI authenticated, macOS 26 Apple Silicon.

   > **Why the checksum matters.** `macapp/install-zero.sh` downloads
   > `releases/latest/download/zero.dmg`, which is a moving target, then fetches
   > `zero.dmg.sha256` from the same release and refuses to install a DMG that
   > doesn't match. That is what makes "the install command always gets the latest
   > build" safe rather than trusting whatever bytes arrive. If a release ships
   > without the `.sha256`, the installer says so out loud and continues on the
   > app-signature check alone — it does not pretend to have verified anything.

## The install URL

`https://zero.headless.com/install` is the command on the homepage. It is a **302
redirect** to `macapp/install-zero.sh` on `master` (see `landing/nginx.conf`), not
a copy baked into the site image. So:

- An installer fix reaches users as soon as it lands on `master`. No site redeploy.
- `macapp/install-zero.sh` stays the single source of truth.
- **But**: anything unpushed is invisible to users. After changing the installer,
  `git push origin master`, then confirm what people actually get:

  ```bash
  curl -fsSL https://zero.headless.com/install | head -20   # expect your change
  ```

`/install.sh` redirects to the GitHub blob view, for reading it in a browser first.

Rebuild and smoke-test the site image with `landing/build.sh`, which boots the
container and fails if `/install` stops redirecting to a parseable script.

### Deploying the site

`zero.headless.com` runs on **`production-server`** (GCP `drewl-366215`,
`us-central1-a`, 34.66.84.21). That box is a **Dokploy** host running ~30 unrelated
production containers behind Traefik, so never restart the host, Traefik, or anything
you did not build.

The site is a Dokploy **compose** app (`composeId u2SP2b5035tm1yaHVNcH8`, project
`zero-zerolanding-m7cxtx`) with `sourceType: raw`: the compose file is stored in
Dokploy's Postgres, and it runs a prebuilt image. It does **not** auto-deploy from
git, despite what an old CHANGELOG entry claims. Traefik routes
`Host('zero.headless.com')` to the container's port 80 and terminates TLS.

Deploying is: build the image on the server, point that one compose service at the
new tag, recreate just that service.

```bash
# 1. Ship the landing files (Docker needs them inside the build context)
SHA=$(git rev-parse --short HEAD)
tar czf /tmp/zero-landing.tgz -C landing \
  index.html privacy.html terms.html og.png robots.txt sitemap.xml llms.txt \
  nginx.conf Dockerfile
gcloud compute scp /tmp/zero-landing.tgz production-server:/tmp/ \
  --zone=us-central1-a --project=drewl-366215 --tunnel-through-iap

# 2. On the server: build, smoke-test, then swap the image tag
gcloud compute ssh production-server --zone=us-central1-a --project=drewl-366215 \
  --tunnel-through-iap --command="
    B=/tmp/zero-landing-build; rm -rf \$B; mkdir -p \$B
    tar xzf /tmp/zero-landing.tgz -C \$B
    sudo docker build -t zero-landing:$SHA \$B
    D=/etc/dokploy/compose/zero-zerolanding-m7cxtx/code
    sudo cp \$D/docker-compose.yml /root/zero-compose-backup.yml
    sudo sed -i 's|image: .*|image: zero-landing:$SHA|' \$D/docker-compose.yml
    cd \$D && sudo docker compose up -d
  "

# 3. Verify the LIVE url, not the local one
curl -fsSL https://zero.headless.com/install | head -5
```

Also update the stored compose in Dokploy's DB, or its UI will still show the old
image and a redeploy from the UI would revert you:

```sql
update compose set "composeFile" =
  'services: {zero-landing: {image: ''zero-landing:<SHA>'', restart: unless-stopped,
   environment: {HOST: ''0.0.0.0'', PORT: ''80''}}}'
where "composeId" = 'u2SP2b5035tm1yaHVNcH8';
```

**Rollback:** the previous image stays on the server. Restore
`/root/zero-compose-backup.yml` over the compose file and `docker compose up -d`.

`landing/build.sh` smoke-tests the image locally first and `landing/deploy.sh` wraps
the generic ssh/registry flow; both refuse to proceed if `/install` stops returning a
parseable script.

---

## Known caveats

- **Unsigned / un-notarized.** The DMG is not code-signed or notarized. Users must
  right-click → Open on first launch to bypass Gatekeeper.
- **No auto-update.** Users download new releases from the GitHub releases page
  manually. The in-app version display (overflow menu) lets them see what they are
  running.

---

## Regenerating the API docs

The `docs/api/openapi.json` is hand-written and committed. There is no codegen
step. To preview the Scalar render locally, open `docs/api/index.html` in a browser
while `python3 lib/keeper_server.py` is running (so the CDN script loads; the file
fetches `openapi.json` from the same directory via a relative URL, which works in
any browser that can load local files from a `file://` origin or a local server).

```bash
# Quickest preview (Python's built-in server, no install needed)
python3 -m http.server 8080 --directory docs/api
open http://localhost:8080
```
