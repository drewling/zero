# Launch announcement draft

## Subject
zero is faster when you open it, and steadier after it runs

## Draft

This release is mostly about getting out of zero's own way.

zero is meant to disappear after it has kept the few emails that still need you. But parts of that experience were doing work twice, doing it for mail that had already left the Inbox, or building a settings screen before you asked to see it.

We measured the fixes on the same live Gmail account and the same Mac used for the investigation. On that account, the inbox pipeline now reaches a 2.3-second steady state using 18 Gmail quota units, after earlier runs could still be reading when they hit a 10-minute timeout. That is not a promise for every inbox. A first pass still has to read mail it has never seen, and its time depends on mailbox size and Gmail's limits.

Opening zero's panel was also measured at 538 ms before this change and 48, 57, and 50 ms across three open-close cycles afterwards on that machine. The change does not cut corners in the panel. It waits to build settings tabs until you visit them, then keeps visited tabs ready so their state and scroll position remain intact.

The release also fixes work that could make a run look successful without actually clearing the Inbox. zero now collects every Inbox-bearing message before archiving a thread, and its mirror sync drops threads that a run has already archived instead of downloading them again. Safety remains the same: archiving removes the Inbox label, adds a dated recovery label, and never deletes mail.

The important part is not a benchmark. It is that zero can get back to being quiet: it should finish its work, show the few things that still need you, and leave the rest alone.

## Measurement note

- Inbox results: one live account with about 3,000 Inbox threads, same verdicts before and after.
- Panel results: one Mac, measured with an opt-in main-thread hitch monitor across three open-close cycles.
- These are observed results from the investigation, not a guaranteed runtime for every account or machine.

## Release-version placeholder

Add the release version here after the release planner confirms it. Do not publish this draft until then.
