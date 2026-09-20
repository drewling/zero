# zero 1.7.0 launch announcement

## Subject
zero 1.7.0 is faster when you open it, and steadier after it runs

## Draft

zero 1.7.0 makes zero faster and steadier at its one job: leave you with only the email that needs you.

zero works quietly. We found it repeating work, including after it had already set mail aside. That slowed some runs and the app.

On the same live Gmail account used for the investigation, with about 3,000 Inbox threads, zero reached a 2.3-second steady state after its first pass. On the same Mac, opening the panel measured 538 ms before the change, then 48, 57, and 50 ms across three open-close cycles afterwards.

Those are observed results, not a promise for every inbox or machine. A first pass still needs to read mail zero has not seen before, and timing varies with your mailbox and Gmail.

The release also fixes cases where a run could look complete without fully clearing qualifying mail from the Inbox. zero still never deletes anything. It removes the Inbox label, adds a dated recovery label, and leaves your mail in All Mail.

The point is simple: zero should finish its work, show you the few things that still need you, and then get out of your way.

## Optional measurement notes

- Inbox result: one live account with about 3,000 Inbox threads, using the same verdicts before and after.
- Panel result: one Mac, measured with an opt-in main-thread hitch monitor across three open-close cycles.
- These are observed results from the investigation, not a guaranteed runtime for every account or machine.
