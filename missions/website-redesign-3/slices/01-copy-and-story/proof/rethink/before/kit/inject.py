#!/usr/bin/env python3
"""Inline kit/icons.svg into every comp page between <!--icons:start--> and <!--icons:end-->,
and give every <svg class="px ..."><use href="#name"/> the symbol's viewBox so it has the right aspect ratio
(an outer <svg> with no viewBox defaults to 300x150 and pushes labels away).
The sprite is inline (not fetched), so the pages render complete without JavaScript.
Run from proof/comps:  python3 kit/inject.py"""
import re
from pathlib import Path

here = Path(__file__).resolve().parent
sprite = (here / "icons.svg").read_text().strip()
boxes = dict(re.findall(r'<symbol id="([\w-]+)" viewBox="([^"]+)"', sprite))
pat = re.compile(r"<!--icons:start-->.*?<!--icons:end-->", re.S)
use = re.compile(r'<svg class="(px[^"]*)"(?: viewBox="[^"]*")?([^>]*)><use href="#([\w-]+)"/>')
for page in sorted(here.parent.glob("*/*.html")):
    s = page.read_text()
    if "<!--icons:start-->" not in s:
        continue
    s = pat.sub(lambda _: f"<!--icons:start-->{sprite}<!--icons:end-->", s)
    s = use.sub(lambda m: f'<svg class="{m[1]}" viewBox="{boxes.get(m[3], "0 0 16 16")}"{m[2]}><use href="#{m[3]}"/>', s)
    page.write_text(s)
    print("injected", page.relative_to(here.parent))
(here / "boxes.js").write_text("window.ZmBoxes=" + str(boxes).replace("'", '"') + ";\n")
