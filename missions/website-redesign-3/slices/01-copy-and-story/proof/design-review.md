# Design review: COPY v2 against the one-bit comps (slice 02)

Reviewer: design-lead@zero, 2026-09-29 ~21:15Z. Reviewed `COPY.md` DRAFT v2 and `OUTLINE.md` v1. Gate A still sits with the owner. This note checks fit only.

## Verdict: fits. Comps are built on v2 as written.

The six-section order matches the slice 02 section plan one for one. Every h2 reads on its own, so none of them needs a cryptic window title to carry meaning. The hero now says Gmail, inbox and Mac in the first line.

## How each section lands in the one-bit world

| Section | Copy v2 heading | Design (slice 02) | Fit note |
|---|---|---|---|
| 1 Hero | Clean up your Gmail inbox on your Mac. | Menu bar with the real tray icon, the zero popover showing the 4 rows, the dated Archived folder and an empty Trash | 7 words, which set in 3 lines of Pixelify at 1440 and 4 at 390. The panel copy (4 rows, "4 things still need you") is used verbatim. |
| 2 Demo | See what stays. See what gets archived. | A Finder-style Inbox window with 12 rows. 4 stay, 8 are dragged into "Auto-Archived 2026-09-29". The static end state shows both destinations, labelled. | The 4 example sentences map onto 4 of the rows. The caption goes directly under the window. |
| 3 Decisions | Keep mail that needs your reply or action. | "Stays" and "Archived" as two index cards, each listing reasons, plus a Settings → Rules window excerpt | The app's real tags (Needs reply, Action required) are the visual vocabulary. No reasons UI is invented. |
| 4 Undo | Undo an archive. Nothing is deleted. | zero's Undo tab (a day row with Restore all) next to a Gmail All Mail search for the dated label | Every label drawn is a real app string: "Restore all" and "N set aside · account". |
| 5 Disclosures | Know what you connect, share and pay for. | One "Get Info" window with four fields: Gmail access, Email data, Reply drafts, Cost | Full text is visible, with no accordion. |
| 6 Install | Install zero on your Mac. | Terminal window with the warning printed above the prompt, then the three next steps | The command is exact. |

## Exact asks (small, none blocking)

1. **Demo row strings.** The demo needs about 8 archived rows in addition to your 4 kept ones. I drafted these fictional ones in the comp:
   - "Weekly digest: 12 new posts"
   - "Your receipt from Northwind Coffee"
   - "Quick question about your pipeline" (cold sales)
   - "Your order has shipped"
   - "New sign-in to your account"
   - "Webinar: scaling outbound in 2027"
   - "Statement ready: September"
   - "Re: Lunch Thursday?", with your own message last

   Please own these words or replace them. They count toward the word budget.
2. **Hero secondary route.** v2's hero has only the primary CTA. The comps add a small text link, "Read the installer first", beside it. It is the same `/install.sh` route the old hero had, and it tells a cautious visitor that the script is readable. Keep it or cut it; either works for the layout.
3. **Window titles.** Each window needs a short, plain title, which sits on a white plate over the stripes. I used: `zero` (the popover has none, since it's a menu-bar popover), `Inbox`, `Auto-Archived 2026-09-29`, `Rules`, `Undo`, `zero Info`, `Terminal`. They are nouns, not headlines. Flag any you want to count or change.
4. **Demo caption.** "Illustration. Made-up names and email subjects, not a result promised for your inbox." fits under one window at 1440 and wraps to 3 lines at 390. Fine as is.
