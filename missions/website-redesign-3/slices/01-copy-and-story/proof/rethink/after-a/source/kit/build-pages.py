#!/usr/bin/env python3
"""Build the two whole-page comps (page-a/, page-b/) from approved hero B plus Draft3 section copy.

Hero B is taken VERBATIM from hero-b/index.html (its style block, menu bar, hero section and hero script), so the
approved hero cannot drift. Two changes only: the menu bar's "How it works" link points at #how (the demo section
it pointed at is cut in both outlines) and the page-level heading face comes from page.css (option T3).
Section words are Draft3 (slices/01-copy-and-story/proof/rethink/SECTION-COPY.md @ 496d985): the COPY-A / COPY-B,
OBJECT-COPY and RULES-B-COPY blocks. The acceptance script checks the rendered words against those blocks.
Run from proof/comps:  python3 kit/build-pages.py && python3 kit/inject.py"""
import re
from pathlib import Path

comps = Path(__file__).resolve().parent.parent
hero_src = (comps / "hero-b" / "index.html").read_text()
copy_src = (comps.parents[2] / "01-copy-and-story" / "proof" / "rethink" / "SECTION-COPY.md").read_text()


def grab(pat, s=hero_src):
    m = re.search(pat, s, re.S)
    assert m, pat
    return m.group(1)


hero_style = grab(r"<style>(.*?)</style>")
header = grab(r"(<header class=\"menubar\">.*?</header>)").replace('href="#demo"', 'href="#how"')
hero = grab(r"(<section class=\"hero desktop\" id=\"hero\".*?</section>)")
hero_script = grab(r"<script src=\"../kit/motion.js\"></script>\s*(<script>.*?</script>)")

# the Rules excerpt, verbatim from the copywriter's block (the policy lines between "Save" and the end marker)
rules_block = grab(r"<!-- RULES-B-COPY-START -->(.*?)<!-- RULES-B-COPY-END -->", copy_src).strip("\n")
policy = rules_block.split("\nSave\n", 1)[1].strip("\n")
esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
policy_html = "".join(f'<span class="ln">{esc(line) if line else ""}</span>' for line in policy.split("\n"))

RARR = "→"
q = lambda t: t.replace("'", "’")  # typographic apostrophes; the counter treats ’ and ' alike

ON = ' class="on"'
TABS = lambda on: '<div class="tabs" aria-hidden="true">' + "".join(
    f'<span{ON if t == on else ""}>{t}</span>' for t in ["Open loops", "Accounts", "Undo", "Settings"]) + "</div>"
BAR = lambda t: f'<div class="bar"><span class="box close" aria-hidden="true"></span><span class="t">{t}</span><span class="box zoom" aria-hidden="true"></span></div>'
SBAR = ('<div class="sbar" aria-hidden="true"><svg class="px" viewBox="0 0 11 9"><use href="#sb-up"/></svg>'
        '<span class="track"><span class="thumb"></span></span><svg class="px" viewBox="0 0 11 9"><use href="#sb-down"/></svg></div>')

ROWS = [("Weekly newsletter", "Fieldnotes · 2d"), ("Coffee receipt", "Northwind · 2d"), ("Sales introduction", "SalesCo · 3d"),
        ("Shipping confirmation", "Parcel · 3d"), ("Webinar invitation", "Workshop · 4d")]
UNDO = f'''<figure class="obj undo-obj" id="undo-win">
      <div class="win">
        {BAR("Undo")}
        {TABS("Undo")}
        <div class="batch">
          <div class="bhead">
            <span class="chv" aria-hidden="true"><svg class="px chevd" viewBox="0 0 7 4"><use href="#chevd"/></svg><svg class="px chevr" viewBox="0 0 4 7"><use href="#chev"/></svg></span>
            <span class="bwhen"><b>Tue 29 Sep</b><span>8 set aside · alex@example.com</span></span>
            <span class="btn sm fake">Restore all</span>
          </div>
          <div class="scroller">
            <ul class="urows">
''' + "\n".join(
    f'              <li><span class="uw"><span class="us">{s}</span><span class="uf">{f}</span></span>'
    f'<span class="ub{" hot" if i == 4 else ""}" aria-hidden="true"><svg class="px" viewBox="0 0 15 14"><use href="#restore"/></svg></span></li>'
    for i, (s, f) in enumerate(ROWS)) + f'''
            </ul>
            {SBAR}
          </div>
        </div>
      </div>
      <p class="balloon" role="note">Put this email back in the inbox</p>
      <figcaption class="caption">Illustration. Made-up mail.</figcaption>
    </figure>'''

RULES = f'''<figure class="obj rules-obj" id="rules-win">
      <div class="win">
        {BAR("Settings")}
        {TABS("Settings")}
        <div class="pane">
          <p class="ph">Rules</p>
          <div class="editor"><pre>{policy_html}</pre>{SBAR}</div>
          <div class="save"><span class="btn sm fake">Save</span></div>
        </div>
      </div>
    </figure>'''

LEDGER_ROWS = [
    ("Google sign-in.", "Connect Gmail through Google in your browser. zero never sees your password. You may see an unverified-app warning because zero hasn't completed Google's app review."),
    ("Sorting data.", "TypeSafe's Jev model receives sender, subject, a preview of up to 160 characters, whether you sent the latest message and whether you've replied to that sender before, your rules and learned preferences. No zero server receives your email. <a href=\"/privacy.html\">Privacy policy</a>."),
    ("Sorting cost.", "Bring your own Jev key, billed by TypeSafe. See <a href=\"https://docs.typesafe.ai/models\">TypeSafe pricing</a>. The app is free and open source under AGPL-3.0."),
    ("Optional drafts.", "Claude Code, or another AI coding tool you already use, can draft replies using its account and billing. Its provider receives thread previews, sent-mail samples, writing preferences and saved profile context. Review before <b class=\"ui\">Send reply</b>. Drafts never send automatically."),
    ("Installer.", "zero is not notarized by Apple. The installer may add Homebrew, Python, Node and the Google Workspace CLI. It adds Claude Code if no supported coding tool is installed."),
]


def ledger(lede=""):
    rows = "\n".join(f'          <div class="row"><dt class="k">{k}</dt><dd class="v">{q(v)}</dd></div>' for k, v in LEDGER_ROWS)
    lede_html = f"\n    <p>{lede}</p>" if lede else ""
    return f'''<section class="band ledger" id="install" aria-labelledby="before">
  <div class="txt">
    <div class="icon appicon"><svg class="px" viewBox="0 0 32 28" aria-hidden="true"><use href="#app"/></svg><span class="lbl">zero</span></div>
    <h2 id="before">Before you install.</h2>{lede_html}
  </div>
  <div class="win info">
    {BAR("Before you install")}
    <dl class="rows">
{rows}
    </dl>
  </div>
</section>'''


def install(h2, after):
    return f'''<section class="band ink" id="command" aria-labelledby="h-install">
  <div class="txt">
    <h2 id="h-install">{q(h2)}</h2>
    <p>{after}</p>
  </div>
  <div class="term-wrap">
    <div class="win" id="term">
      {BAR("Terminal")}
      <pre><span class="p" aria-hidden="true">% </span><code>curl -fsSL https://zero.headless.com/install | bash</code> <span class="cursorblk" aria-hidden="true"></span></pre>
      <div class="foot"><button class="btn" type="button" id="copy">Copy command</button></div>
    </div>
  </div>
</section>'''


def band(cls, id_, h_id, h2, paras, obj, extra_id=""):
    ps = "\n    ".join(f"<p>{q(p)}</p>" for p in paras)
    return f'''<section class="band {cls}" id="{id_}" aria-labelledby="{h_id}">
  <div class="txt">
    <h2 id="{h_id}">{q(h2)}</h2>
    {ps}
  </div>
  <div class="field">
    {obj}
  </div>
</section>'''


ui = lambda t: f'<b class="ui">{t}</b>'
A_sections = [
    band("split-r", "undo", "how", "See what went into the archive.", [
        "Start a run from zero's menu bar. The app sorts the Gmail accounts you connect. Keep reading your connected Gmail account in Gmail or Apple Mail.",
        f"An AI model uses your rules to keep replies you owe, direct requests, payment problems, legal matters and consequential deadlines. Receipts, newsletters and cold sales may be archived. Change the rules in {ui('Settings ' + RARR + ' Rules')}. Sorting leaves starred mail alone and keeps threads it can't decide about.",
        f"Check your first few runs. The model can make mistakes. In zero's {ui('Undo')} tab, restore one email or choose {ui('Restore all')} for a day's archives. Nothing is deleted: archived mail stays searchable in Gmail's {ui('All Mail')} under a dated recovery label.",
    ], UNDO),
    ledger(),
    install("Install when you're ready.",
            f'Open zero, connect Gmail and save your <a href="https://console.typesafe.ai/keys">Jev key</a> in {ui("Settings " + RARR + " Sorting engine")}. Or download from <a href="https://github.com/drewling/zero/releases">GitHub Releases</a>.'),
]
B_sections = [
    ledger("Read your connected Gmail in Gmail or Apple Mail."),
    band("split-r", "how-band", "how", "Choose what needs to stay.", [
        "Run zero from its menu bar to sort connected Gmail accounts. AI applies your rules. Starred mail stays untouched. Uncertain threads stay in your inbox. Check your first runs: the model can make mistakes.",
    ], RULES),
    band("split-l", "undo", "h-undo", "Restore archived mail.", [
        f"In zero's {ui('Undo')} tab, restore one email or a day's archives with {ui('Restore all')}. Nothing is deleted. Find archived mail in Gmail's {ui('All Mail')} under a dated recovery label.",
    ], UNDO),
    install("Ready to install?",
            f'Open zero, connect Gmail, then add your <a href="https://console.typesafe.ai/keys">Jev key</a> in {ui("Settings " + RARR + " Sorting engine")}. Or download from <a href="https://github.com/drewling/zero/releases">GitHub Releases</a>.'),
]

FOOTER = '''<footer>
  <span class="brand"><svg class="px" viewBox="0 0 16 15" aria-hidden="true"><use href="#check"/></svg>zero</span>
  <span>AGPL-3.0</span>
  <a href="https://github.com/drewling/zero">Source</a>
  <a href="/privacy.html">Privacy</a>
  <a href="/terms.html">Terms</a>
</footer>'''

for name, label, sections in [("page-a", "A · recovery-first", A_sections), ("page-b", "B · risk-first", B_sections)]:
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page {label} · zero redesign 3 whole-page comp (draft)</title>
<link rel="stylesheet" href="../kit/kit.css">
<link rel="preload" href="../kit/chicagoflf.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../kit/geist.woff2" as="font" type="font/woff2" crossorigin>
<!-- generated by kit/build-pages.py: do not edit by hand. Hero B styles copied verbatim from hero-b/index.html -->
<style>{hero_style}</style>
<link rel="stylesheet" href="../kit/page.css">
</head>
<body class="page {name}">
<!--icons:start--><!--icons:end-->
<p class="draft-flag">DRAFT comp · page {label} · Draft3 · not approved</p>
{header}

<main id="top">
{hero}

{chr(10).join(sections)}
</main>
{FOOTER}

<script src="../kit/motion.js"></script>
<!-- hero B story, verbatim -->
{hero_script}
<script src="../kit/sections.js"></script>
</body>
</html>
'''
    out = comps / name / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print("built", out.relative_to(comps))
