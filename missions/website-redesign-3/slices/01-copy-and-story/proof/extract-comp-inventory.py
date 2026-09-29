#!/usr/bin/env python3
"""Read-only comp text inventory, leaving decorative visible ARIA-hidden text in."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys


class Inventory(HTMLParser):
    def __init__(self, omit_header=False):
        super().__init__(convert_charrefs=True)
        self.omit_header = omit_header
        self.stack = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        inherited = self.stack[-1][1] if self.stack else False
        classes = set(attrs.get("class", "").split())
        skip = inherited or tag in ("head", "style", "script", "svg")
        skip = skip or bool(classes & {"draft-flag", "sr-only"})
        skip = skip or (self.omit_header and tag == "header")
        if tag not in ("meta", "link", "br", "img", "hr", "input", "path", "use"):
            self.stack.append((tag, skip))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        if not (self.stack and self.stack[-1][1]) and text.strip():
            self.rows.append(" ".join(text.split()))


def extract(filename, omit_header=False):
    file = Path(filename)
    data = file.read_bytes()
    parser = Inventory(omit_header)
    parser.feed(data.decode("utf-8"))
    return {"path": str(file), "sha256": hashlib.sha256(data).hexdigest(),
            "textNodes": parser.rows}


if __name__ == "__main__":
    print(json.dumps({"hero": extract(sys.argv[1]),
                      "sections": extract(sys.argv[2], omit_header=True)},
                     ensure_ascii=False))
