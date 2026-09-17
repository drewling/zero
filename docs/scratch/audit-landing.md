# Landing Page Audit — Against New Business Model

**Date:** 2026-09-17
**Scope:** `landing/index.html` (1,342 lines, 164KB), `landing/privacy.html`, `landing/terms.html`, `LICENSE`
**New business model:** free + open source + one-line CLI install (no App Store, no Apple Developer account, no notarization, no DMG-drag). Bring-your-own-API-key (Jev from TypeSafe AI, or the user's already-installed local Claude Code / Codex / opencode CLI). No server. A $4.99/mo hosted tier comes LATER, not now.

---

## 1. Structure map (landing/index.html, in order)

1. **`<head>` meta + JSON-LD** (L1–133): SEO/OG/Twitter meta tags and `schema.org` structured data (`SoftwareApplication`, `Organization`, `WebSite`, `FAQPage`). Not visible content, but crawled by search engines and AI answer engines — carries real factual claims (price, OS, download URL, credentials model).
2. **`nav`** (L736): logo/wordmark, nav links, GitHub star-count button. No distinct visible CTA button beyond nav links (star button aside).
3. **`#hero`** (L766–816): H1 "An inbox you can finally ignore." Lead paragraph. CTA row: primary button **"Download for macOS"** (links to GitHub Releases) + secondary anchor link **"How it stays safe"** (`#trust`). Requirements pill row: `macOS 26` / `Source-available` / `Your own Google + Claude` / `Free`. Includes a fake app-panel screenshot mock (the "kept 3 things this morning" demo UI).
4. **`.trust-strip`** (L824–841): 3 quick trust badges in a row — "Nothing is deleted. Ever." / "Runs on your keys. No server." / "Source-available. Read it." No CTA.
5. **`#problem`** (L844–855): Pain-point narrative ("You don't have an email problem..."). No CTA.
6. **`#howitworks`** (L856–907): "Three questions, asked about every thread, every morning" — decision logic breakdown (3 numbered items) plus an animated before/after inbox visual (27 threads → 3 kept). No CTA.
7. **`#trust`** (L908–966): Section heading "Nothing is ever deleted. That's the whole design." Bento grid of 5 trust cards: *Reversible by construction*, *Your keys. Your machine.*, *Ambient, not another inbox*, *Judgment in plain language*, **"Source-available"** (reads exactly what runs on your inbox). Followed by a cred-pill row: "Your Google / Your Claude / Your Mac / We can't see your mail." No CTA (this section is the anchor target of the hero's secondary CTA).
8. **`#reply`** (L968–996): "Drafts in your voice. On demand. Never on its own." Fake draft-panel mock, explains draft feature never auto-sends. No CTA.
9. **`#multiaccount`** (L1001–1029): "Every account. One calm." Multi-Gmail-account demo cards. No CTA.
10. **`#aiengine`** (L1030–1047): "Works with your AI engine." Provider chips: **Claude · default (active)**, Codex, Hermes, Other agent CLIs. Copy: "You supply the API key, and it stays on your machine." No CTA — but this section's chip pattern is the most reusable component for the new BYO-key story.
11. **`#faq`** (L1048–1095): "What people ask before trusting it." 6 `<details>` Q&As, content duplicates the JSON-LD FAQ block (L80–127) nearly verbatim. No CTA.
12. **`#cta`** (L1096–1116): Final CTA. Eyebrow "Free. Open. Yours." H2 "Let your inbox keep itself." Buttons: **"Download for macOS"** (primary) + "View on GitHub" (secondary). Repeats requirement pills: `macOS 26` / `Source-available` / `Your own Google + Claude`.
13. **`<footer>`** (L1117+): Brand blurb + three link columns — *Product* (Download, How it works, Safety, FAQ), *Project* (GitHub, Changelog, Releases), *Trust* (Private by design, AI providers, Privacy, Terms).
14. **Closing `<script>`** (L1161 onward): scroll-reveal IntersectionObserver, nav-scrolled state toggle, live GitHub star-count fetch (`api.github.com/repos/drewling/zero`, fails gracefully), assorted "delight" JS.

---

## 2. Every claim that is now wrong or stale

### Credentials / provider model too narrow (Google + Claude only)
- **L7** (meta description): *"Runs locally on your own Google and Claude keys."* — Wrong: doesn't mention Jev (TypeSafe AI) or reuse of an already-installed local Claude Code / Codex / opencode CLI.
- **L27** (Twitter description): *"private by design: runs on your own Google and Claude keys."* — same issue.
- **L45** (JSON-LD description): *"Runs locally on your own Google and Claude credentials."* — same issue.
- **L59** (JSON-LD featureList): *"Runs locally on your own Google and Claude API keys"* — same issue.
- **L88** (JSON-LD FAQ answer / duplicated at **L1057–1059** visible FAQ): *"zero runs entirely on your own Mac using your own Google and Claude credentials."* — same issue, plus assumes macOS.
- **L791** (hero-req pill): *"Your own Google + Claude"* — too narrow; needs to become something like "Your own AI (Jev, Claude Code, Codex, opencode)."
- **L1111** (final-CTA req pill): same text, repeated.
- **L1034–1042** (`#aiengine` section) is closest to correct already — mentions Claude/Codex/Hermes/Other agent CLIs — but still frames Claude as "default" and doesn't mention Jev at all. This section should be the template the rest of the page's credential language is rewritten to match.

### Download / install flow implies a signed macOS app, DMG, or App Store distribution
- **L47** (JSON-LD): `"downloadUrl": "https://github.com/drewling/zero/releases/latest"` — implies a downloadable release artifact (DMG/binary), not a one-line CLI install.
- **L780–783** (hero primary CTA): button text **"Download for macOS"**, links to GitHub Releases. Wrong verb and wrong destination entirely for a `curl | sh` / one-liner install flow. This is the single most important place to fix (see Section 3).
- **L1103–1106** (final CTA): duplicate of the same "Download for macOS" button/link.
- **Footer** "Download" link (in Product column, near L1132) also points at GitHub Releases — same issue.
- **`landing/terms.html` L69**: *"A Mac that meets the requirements on the [download page](/)."* — presupposes a "download page" concept; should be reworded around install requirements instead.

### macOS-version gating stale for a CLI tool
- **L44** (JSON-LD): `"operatingSystem": "macOS 26"`.
- **L112** (JSON-LD FAQ, duplicated **L1071–1073** visible FAQ): *"macOS 26, a Google account with your own API credentials, and a Claude API key."*
- **L790** (hero-req pill): `macOS 26`.
- **L1111** (final-CTA req pill): `macOS 26` repeated.
All four instances hard-gate on a specific macOS version. If the new model is a CLI (potentially cross-platform, or at least not tied to a specific signed-app macOS release cadence), this framing is stale and should be softened or generalized.

### "Source-available" vs. actually claiming "open source" — conflicts with LICENSE
- **L790** (hero-req pill): `Source-available`.
- **L836** (trust-strip): *"Source-available. Read it."*
- **L953–957** (trust bento card, `<h3>Source-available</h3>`): *"Read exactly what runs on your inbox. No compiled mystery, no hidden logic, the keep-rule is a prompt you can inspect and edit."*
- **L1111** (final-CTA req pill): `Source-available` repeated.
- **L104** (JSON-LD FAQ) / **L1052–1054** (visible FAQ, "What does zero cost?"): *"zero is free and source-available. You pay only for your own Claude API usage, which for a typical inbox is a few cents a day."*

**These currently say "source-available," which is actually the factually correct term today — but it directly conflicts with the owner's stated intent to launch this as "open source."** See the dedicated LICENSE section below: this is a real, structural conflict, not just a copy nit.

### Pricing / "free" framing needs the $4.99/mo hosted tier explicitly deferred
- **L49–54** (JSON-LD `isAccessibleForFree: true`, `offers.price: "0"`) is currently accurate for the free/BYO-key model and can stay, but there is no forward-looking mention that a paid hosted tier is coming later — not required to add, but worth flagging as an option since the business model doc explicitly says "$4.99/mo hosted tier comes LATER, not now." No page claim actively contradicts this (good — nothing currently promises a hosted tier), so this is a non-issue for *removal* but an opportunity if the team wants to tease it.
- **L791** and **L1111** hero-req/final-CTA pills also carry the word "Free" — this remains accurate under the new model (BYO-key means zero itself is free; only the user's own AI usage costs money) and does **not** need to change.

### Miscellaneous
- **L47** `softwareHelp: "https://github.com/drewling/zero"` — fine, no change needed.
- **L88 / L1057–1059** FAQ answer says "your own Mac" specifically — ties privacy claim to macOS; should be generalized if the CLI is cross-platform, or left as-is if truly macOS-only, but worth an explicit decision.
- **`landing/privacy.html` L81**: *"zero is made by Tayo Onabule (Drewl). It is a downloadable desktop app, not a hosted service."* — "downloadable desktop app" framing again implies DMG/binary; should shift to "a CLI tool you install locally."
- **`landing/privacy.html` L128**: *"zero is open source, so every change is also visible in its public history."* — **this file already asserts "open source" today**, which is the term the owner wants, but it's currently untrue given the PolyForm-NC license (see below), and it's inconsistent with index.html's "source-available" language. These two files disagree with each other right now.

---

## 3. Where the install one-liner should live

The **only** install-adjacent UI elements on the entire page today are:
- Hero primary CTA button, **"Download for macOS"** (L780–783), linking to `https://github.com/drewling/zero/releases/latest`.
- Final-CTA section's duplicate of the same button (L1103–1106).
- Footer "Download" link, same destination.

All three currently drive a "go to GitHub Releases and download an artifact" flow. This is exactly where a `curl -fsSL https://.../install.sh | sh` (or `brew install zero` / npm one-liner, whatever the actual chosen mechanism is) install command needs to replace the button's destination and framing.

Good news: the page already has a ready-made visual component for exactly this — the `.code-snippet` element used at **L933** inside the "Reversible by construction" trust card:
```html
<div class="code-snippet">label:<strong>"🗄️ Auto-Archived 2026-06-25"</strong>&nbsp;&nbsp;<span class="comment">// one search restores a whole run</span></div>
```
This styling pattern (monospace, inline code chip with a dimmed comment) should be lifted and reused for a hero-level install snippet, e.g. a copyable `<div class="code-snippet">curl -fsSL https://zero.dev/install.sh | sh</div>` with a copy-to-clipboard affordance, replacing the current "Download for macOS" button as the primary hero CTA. The same treatment should replace the final-CTA button.

---

## 4. Technical facts about the page

- **Hand-written single HTML file**: 1,342 lines, 164KB, with all CSS inline in a single `<style>` block starting at **L137**, and all JS inline in `<script>` blocks at **L731** and **L1161** onward. No separate `.css` or `.js` files.
- **No build step**: no `package.json`, bundler config, or build tooling found under `landing/`. The HTML file is edited and deployed as-is.
- **Deployment**: `landing/Dockerfile` is a minimal `nginx:alpine` image that simply `COPY`s the static files (`index.html`, `privacy.html`, `terms.html`, `og.png`, `robots.txt`, `sitemap.xml`, `llms.txt`) into `/usr/share/nginx/html/` and serves them with nginx. No CI/build pipeline is involved — rebuilding the Docker image after editing the HTML is sufficient to deploy.
- **How to edit safely**: because it's one big self-contained file, direct text/copy edits are low risk. Two things to watch:
  1. The JSON-LD block (**L34–133**) duplicates several claims that also appear as visible HTML further down the page (notably the FAQ section, **L1048+**, and the `SoftwareApplication` description/featureList). Any copy change (credentials, pricing, OS requirement, download flow) must be made in **both** places to avoid the page contradicting its own structured data.
  2. `landing/privacy.html` and `landing/terms.html` are separate files with their own overlapping claims (see Section 2) and must be updated in sync with `index.html`.
- **Responsive**: yes — 6 `@media` query blocks are present in the stylesheet, so the layout does adapt at breakpoints. Visual quality of the responsive behavior was not verified in-browser as part of this audit (investigate-only, no rendering check performed).
- **JS dependencies**: none. No external libraries or CDNs. The only network call the page makes client-side is a `fetch('https://api.github.com/repos/drewling/zero', ...)` for the live GitHub star count (L1183–1194), which fails silently and gracefully if rate-limited or blocked.

---

## 5. Honest design read

**Genuinely good, should survive the rewrite:**
- The hero "kept 3 things this morning" app-panel mock — concrete, specific, sells the value prop without words.
- The `#howitworks` before/after inbox visual (27 → 3 threads) — this is the single best piece of product storytelling on the page and needs no changes tied to the business-model pivot.
- The `#trust` bento grid layout and its restrained dark visual language.
- The `#aiengine` provider-chip pattern (**L1034–1042**) — already structured exactly right for "bring your own AI" messaging; just needs Jev added as a chip and the "default" framing reconsidered.
- The `.code-snippet` component (**L933**) — reusable almost as-is for the install one-liner.
- Scroll-reveal and nav-scroll JS polish — subtle, no dependency bloat, no reason to touch.
- Overall dark theme, spacing, and restraint — good taste, not overdesigned.

**Filler / lower-value, candidates to cut or simplify:**
- The `#faq` section (**L1048–1095**) is close to pure duplication of the JSON-LD FAQ (**L80–127**) with no additional visual value beyond being clickable `<details>` — fine to keep functionally, but not "content design," just a copy of the same six answers already carried in structured data.
- Four separate instances of "Source-available" (**L790, L836, L953–957, L1111**) and three of "macOS 26" (**L790, L1071–1073, L1111**) are the same claim repeated with no variation — once the underlying facts change (license, OS/install story), fixing the *single* text on both should be treated as one edit conceptually, not four independent ones, to avoid drift.
- The multi-account (`#multiaccount`) and reply (`#reply`) sections are solid content but functionally filler relative to the urgent pivot — they don't contain any claims that conflict with the new model and don't need to change at all right now.

---

## LICENSE conflict — blocking prerequisite for "open source" claims

**File:** `LICENSE` (root of repo, 133 lines)
**License:** PolyForm Noncommercial 1.0.0

Direct quotes from the license text:

> "The licensor grants you a copyright license for the software to do everything you might do with the software that would otherwise infringe the licensor's copyright in it **for any permitted purpose**."

> "## Noncommercial Purposes
> **Any noncommercial purpose is a permitted purpose.**"

> "## Personal Uses
> Personal use for research, experiment, and testing for the benefit of public knowledge, personal study, private entertainment, hobby projects, amateur pursuits, or religious observance, **without any anticipated commercial application**, is use for a permitted purpose."

> "## Noncommercial Organizations
> Use by any charitable organization, educational institution, public research organization, public safety or health organization, environmental protection organization, or government institution is use for a permitted purpose **regardless of the source of funding**."

All copyright, distribution, changes/new-works, and patent licenses granted in this document are scoped to "permitted purposes," and the only permitted purposes defined are noncommercial ones (personal use without commercial application, or use by noncommercial/charitable/educational/government organizations). **Commercial use is never a permitted purpose under this license.**

This means PolyForm Noncommercial is, by design, **not an OSI-approved open-source license**. The [Open Source Definition](https://opensource.org/osd) requires (among other things) "no discrimination against fields of endeavor" — i.e., a license cannot restrict commercial use and still be called open source. PolyForm's own project site is explicit that PolyForm Noncommercial is a "source-available" license, not an open-source one, precisely because of this restriction.

**Conflict:** `landing/privacy.html` L128 already says *"zero is open source"* today, while `landing/index.html` correctly (for the current license) says "source-available" in four places. These two files already disagree with each other. If the business decision is to launch "as open source," **the LICENSE file itself must change to an OSI-approved license (MIT, Apache-2.0, BSD, etc.) before or simultaneously with any copy change that calls the project open source.** Simply rewriting the landing page's marketing copy to say "open source" while `LICENSE` remains PolyForm-NC would be a false claim likely to draw immediate, public correction from the developer community (this exact pattern — commercial-restricted licenses marketed loosely as "open source" — is a recurring point of criticism for PolyForm/BSL-style licenses in general). This is flagged as a **blocking prerequisite**, not a simple text edit.
