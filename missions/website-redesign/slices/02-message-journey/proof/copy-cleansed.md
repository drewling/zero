# zero homepage: visitor copy (draft 1)

## Hero

Board: KEEP THE MAIL THAT NEEDS YOU.

Lead: zero is a Mac menu-bar app for Gmail. It keeps conversations that still need your attention and archives the rest. Archived mail stays in Gmail. You can put it back.

Button: Install zero for Mac
Link: Read the installer first

Needs: Apple Silicon Mac, macOS 26 or later, Gmail
Sorting: Your own TypeSafe Jev key. TypeSafe bills you for what you use.
Price: zero is free and open source.

Image caption: The real zero app. Names and subjects are made up.

## What stays

Heading: What stays. What gets archived.

Body: When zero sorts a conversation, it checks it against rules written in plain English. Edit them in Settings. If someone is waiting on you, or something needs action, it stays in your Inbox. The rest is archived.

Body: It gets things wrong sometimes. Check your first few runs before you set a schedule.

Board heading: Kind of mail / Default rule
Rows: Someone is waiting for your reply: Stays. A payment has failed: Stays. A deadline with a consequence: Stays. A receipt or statement: Archived. A newsletter: Archived. Cold sales email: Archived. You sent the last message: Archived.

Board note: These are zero's default rules. This isn't a live inbox, and it isn't a promise. The AI can sort a message wrongly. In the app, mail that stays appears under Waiting on you in Open loops.

## Nothing is deleted

Heading: Nothing is deleted.

Body: When zero archives a conversation, it removes Gmail's Inbox label and adds a recovery label with that day's date. The mail stays in All Mail, and search still finds it.

Label: 🗄️ Auto-Archived YYYY-MM-DD
Label note: This is the label's format. The recovery label is dated for the day.

Put a run back: Open the Undo tab in zero and choose Restore all for that day.
Find it in Gmail: Search for the dated label, or look in All Mail. Archived messages remain in Gmail.
Change what stays: Edit the rules in Settings → Rules.

## Before you install

Heading: Before you install

Body: What zero needs, where your mail goes, and what it costs.

Your Mac: Apple Silicon with macOS 26 Tahoe or later. The installer stops if your Mac can't run it.

Gmail: You sign in to Google from the app. zero never sees your password. Google may warn that the app is unverified because zero hasn't completed Google's app verification.

Jev key: Required. Jev is the TypeSafe AI service that sorts your mail. TypeSafe bills and rate-limits usage on your account.

Your mail: zero runs on your Mac. To sort a conversation, it sends the relevant thread text to Jev. If you ask for a reply draft, that text also goes to the AI provider you picked. The zero project doesn't run a server that receives your email. Privacy policy.

Replies: Drafts are optional. zero sends nothing until you click Send reply. Drafts use the account behind the agent CLI you set up.

The app: Ad-hoc signed. It isn't notarized by Apple or in the App Store. The installer may add Homebrew, Python, Node, the Google Workspace CLI, and Claude Code.

## Install

Heading: Install zero.

Body: Four steps, from Terminal to your first run.

Step 1: Run the installer in Terminal.
Warning: Read this first. zero isn't notarized by Apple, and the installer may add developer tools to your Mac. Read the script before you run it.
Command: curl -fsSL https://zero.headless.com/install | bash
After: The installer checks the download's SHA-256 before it installs. Prefer a manual download? Use GitHub Releases.

Step 2: Connect Gmail.
Open zero from the menu bar and choose Connect your first inbox.

Step 3: Add your Jev key.
In Settings → Sorting engine, choose Get a key, create a key at TypeSafe, paste it in, and click Save.

Step 4: Run it once.
Choose Run zero now. Look at what stayed and what was archived. When you're happy, set a time in Settings → Daily routine.

## Questions

Q: Does my email stay on my Mac?
A: No. zero runs on your Mac, but it sends relevant thread text to TypeSafe's Jev to decide what to keep. If you ask for a reply draft, that text also goes to the AI provider you chose. Both handle it under their own terms. The zero project doesn't run a server that receives your email. Your Google sign-in tokens stay on your Mac. The privacy policy lists what else zero stores there.

Q: What if it archives something important?
A: It can happen. The message stays in All Mail with a dated recovery label. Open Undo in zero and restore that day, or find the message in Gmail yourself.

Q: Can zero send email for me?
A: Only when you tell it to. Ask for a draft, edit it if you want, and click Send reply. zero never sends on its own.

Q: Can I use more than one Gmail account?
A: Yes. Connect each account in zero. Conversations from all of them show up together in Open loops.

Q: What does it cost?
A: zero is free. Sorting uses your TypeSafe Jev key, and TypeSafe bills you for that. Drafts use whatever account is behind your agent CLI. Check both providers' prices before you set a daily run.

## Footer

zero. Free and open source, AGPL-3.0. Source. Privacy. Terms.
