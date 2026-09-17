# Copyright and licence

zero is copyright (c) 2026 Tayo Onabule and contributors.

It is free software, licensed under the **GNU Affero General Public License,
version 3 or later** (AGPL-3.0-or-later). The full licence text is in
[LICENSE](LICENSE), copied verbatim from
<https://www.gnu.org/licenses/agpl-3.0.txt>.

## What this means, in plain English

This is not legal advice, just a plain summary of the terms in `LICENSE`. Where
this summary and `LICENSE` disagree, `LICENSE` wins.

**You can:**

- Use zero for anything, including at work and for commercial purposes.
- Read, modify, and share the source.
- Distribute your modified version.

**You must, if you distribute it or run a modified version as a network service:**

- Release your changes under the AGPL as well.
- Offer your users the corresponding source code. Section 13 is the part that
  makes this apply to software offered over a network, not only to software you
  hand someone as a file.

## Why AGPL and not MIT

zero reads people's email. Two things follow from that:

1. **You should be able to read exactly what runs on your inbox.** The AGPL keeps
   that true for every version anyone runs, not just this one. A closed fork that
   quietly changed what gets archived, or where mail text is sent, would be the
   precise thing this licence prevents.
2. **A hosted version has to stay honest too.** Under MIT, someone could run a
   modified zero as a paid service and never publish the changes. Section 13
   closes that, so any hosted zero owes its users the same transparency.

It also leaves room for a hosted tier: the copyright holder can offer the same
code as a paid service, and that service's source stays available under the same
terms.

## Previous licence

Before 2026-09-17 zero was released under the PolyForm Noncommercial 1.0.0
licence, which is *source-available* rather than open source, because it barred
commercial use. It was relicensed to AGPL-3.0 so that "open source" is accurate
under the [Open Source Definition](https://opensource.org/osd), and so that
people can use zero at work.

Relicensing was straightforward because all the code to date is the copyright of
the single author named above. Contributions from here on are accepted under
AGPL-3.0-or-later, as described in [CONTRIBUTING.md](CONTRIBUTING.md).

## Third-party components

zero runs against tools you install and authenticate yourself, and does not
vendor them:

- the `gws` Google Workspace CLI,
- your chosen AI engine (`claude`, `codex`, `opencode`, or the Jev HTTP API).

Each keeps its own licence and terms. zero neither redistributes them nor changes
their terms.
