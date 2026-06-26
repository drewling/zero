// OnboardingView.swift — the first-run takeover. Shown until at least one Gmail
// account is connected. It states the one job, flags any missing prerequisite
// (python3 / gws / claude) with the exact fix, and connects the first inbox via the
// browser OAuth flow the server already exposes. The app never sees a password.

import SwiftUI
import AppKit   // NSPasteboard — "Set it up with Claude" copies the setup prompt

struct OnboardingView: View {
    @EnvironmentObject var m: KeeperModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
      // Scroll when the content is taller than the panel (prereqs + credentials card +
      // paste box can overflow 640pt), but stay vertically centred when it fits — the
      // minHeight: geo.height trick lets the Spacers expand only when there's room.
      GeometryReader { geo in
        ScrollView {
        VStack(spacing: 0) {
            Spacer(minLength: 30)

            // App mark: the glossy blue squircle + cream check (echoes the icon). It
            // breathes almost imperceptibly so the first screen feels alive, not static.
            RoundedRectangle(cornerRadius: 15, style: .continuous)
                .fill(LinearGradient(colors: [Paper.accentHi, Paper.accent], startPoint: .top, endPoint: .bottom))
                .frame(width: 56, height: 56)
                .overlay(Image(systemName: "checkmark")
                    .font(.system(size: 27, weight: .bold)).foregroundStyle(Color(0.99, 0.99, 1.0)))
                .overlay(RoundedRectangle(cornerRadius: 15, style: .continuous)
                    .strokeBorder(.white.opacity(0.28), lineWidth: 0.75))
                .shadow(color: Paper.accent.opacity(0.45), radius: 12, y: 4)
                .phaseAnimator(reduceMotion ? [1.0] : [1.0, 1.035]) { v, s in v.scaleEffect(s) }
                    animation: { _ in .easeInOut(duration: 2.4) }

            Text("zero")
                .font(.system(size: 21, weight: .semibold)).kerning(-0.2)
                .padding(.top, 16)
            Text("Keeps your inbox at only what still needs you, across every account. Nothing is ever deleted.")
                .font(.system(size: 13)).foregroundStyle(Paper.ink3)
                .multilineTextAlignment(.center).frame(maxWidth: 300).padding(.top, 6)

            // Three quiet trust points — the "why trust this" screen. Hidden during the
            // Google-setup step so that screen does exactly one job (one thing at a time).
            if !m.needsCredentials {
                VStack(alignment: .leading, spacing: 9) {
                    TrustRow(symbol: "arrow.uturn.backward", text: "Reversible by design. Archiving just removes the inbox label, restorable any time.")
                    TrustRow(symbol: "moon.stars", text: "Ambient. It works quietly behind your existing mail apps, once a morning.")
                    TrustRow(symbol: "brain", text: "Judged by an agent reading each thread, not brittle filter rules.")
                }
                .padding(16).glassSurface(13).frame(maxWidth: 320).padding(.top, 20)
            }

            // Missing prerequisites (only if the check ran and found gaps).
            if m.preflight.checked && !m.preflight.allGood {
                VStack(alignment: .leading, spacing: 10) {
                    Text("FIRST, INSTALL").font(.system(size: 10, weight: .semibold)).kerning(0.5)
                        .foregroundStyle(Paper.ink4)
                    if !m.preflight.python { ToolRow(name: "Python 3", cmd: "xcode-select --install") }
                    if !m.preflight.gws { ToolRow(name: "Google Workspace CLI", cmd: "npm i -g @googleworkspace/cli") }
                    if !m.preflight.claude { ToolRow(name: "Claude Code CLI", cmd: "npm i -g @anthropic-ai/claude-code") }
                }
                .padding(14)
                .glassSurface(12, tint: Paper.danger.opacity(0.14))
                .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous).strokeBorder(Paper.danger.opacity(0.22), lineWidth: 0.75))
                .frame(maxWidth: 320).padding(.top, 14)
            }

            Spacer(minLength: 18)

            if m.needsCredentials {
                // gws is installed but there's no Google OAuth client yet — let the
                // user set one up in-app instead of hand-placing client_secret.json.
                CredentialsCard()
            } else {
                // Connect the first inbox. gws is required for the OAuth flow.
                // While the sign-in job is running, show the live message from the
                // server and a Cancel button so the user is never stuck.
                Button { m.addAccount() } label: {
                    HStack(spacing: 7) {
                        if m.isBusy { ProgressView().controlSize(.small).tint(.white) }
                        else { Image(systemName: "plus").font(.system(size: 12, weight: .bold)) }
                        Text(m.isBusy ? "Signing in…" : "Connect your first inbox")
                    }
                }
                .buttonStyle(PrimaryButtonStyle(enabled: m.preflight.gws && !m.isBusy))
                .disabled(!m.preflight.gws || m.isBusy)

                // Cancel is always reachable during a sign-in — the user must be able
                // to back out of a stuck OAuth flow without force-quitting.
                if m.isBusy {
                    if let msg = m.job?.message, !msg.isEmpty {
                        Text(msg)
                            .font(.system(size: 11)).foregroundStyle(Paper.ink4)
                            .multilineTextAlignment(.center).frame(maxWidth: 300)
                            .padding(.top, 6)
                    }
                    if let urlStr = m.job?.authUrl, let url = URL(string: urlStr) {
                        Button("Open the sign-in page") { NSWorkspace.shared.open(url) }
                            .buttonStyle(.plain)
                            .font(.system(size: 11, weight: .medium))
                            .foregroundStyle(Paper.accentSoft)
                            .padding(.top, 2)
                    }
                    Button("Cancel sign-in") { m.cancelJob() }
                        .buttonStyle(GhostButtonStyle())
                        .padding(.top, 8)
                } else {
                    Text("Sign-in opens in your browser. The app never sees your password.")
                        .font(.system(size: 11)).foregroundStyle(Paper.ink4)
                        .multilineTextAlignment(.center).frame(maxWidth: 300)
                        .padding(.top, 10)
                }
            }

            Spacer(minLength: 24)
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, minHeight: geo.size.height)
        }
      }
    }
}

// One-time, skippable first-run step: clear the backlog so the keeper starts from a
// calm inbox. Reversible (lands in Undo). Same glass language as OnboardingView.
struct BacklogStep: View {
    @EnvironmentObject var m: KeeperModel
    @State private var beforeDate = Calendar.current.date(byAdding: .day, value: -30, to: Date()) ?? Date()
    private static let apiFmt: DateFormatter = {
        let f = DateFormatter(); f.dateFormat = "yyyy/MM/dd"; return f
    }()
    private static let humanFmt: DateFormatter = {
        let f = DateFormatter(); f.dateStyle = .medium; return f
    }()

    var body: some View {
        VStack(spacing: 0) {
            Spacer(minLength: 30)

            RoundedRectangle(cornerRadius: 15, style: .continuous)
                .fill(LinearGradient(colors: [Paper.accentHi, Paper.accent], startPoint: .top, endPoint: .bottom))
                .frame(width: 52, height: 52)
                .overlay(Image(systemName: "archivebox")
                    .font(.system(size: 23, weight: .semibold)).foregroundStyle(Color(0.99, 0.99, 1.0)))
                .overlay(RoundedRectangle(cornerRadius: 15, style: .continuous)
                    .strokeBorder(.white.opacity(0.28), lineWidth: 0.75))
                .shadow(color: Paper.accent.opacity(0.45), radius: 12, y: 4)

            Text("Start from a calm inbox")
                .font(.system(size: 19, weight: .semibold)).kerning(-0.2).padding(.top, 16)
            Text("Optionally archive everything older than a date you choose, so zero only weighs what's recent. Nothing is deleted — it's one tap to undo.")
                .font(.system(size: 13)).foregroundStyle(Paper.ink3)
                .multilineTextAlignment(.center).frame(maxWidth: 320).padding(.top, 6)

            VStack(spacing: 12) {
                HStack(spacing: 10) {
                    Text("Archive everything before").font(.system(size: 12.5)).foregroundStyle(Paper.ink2)
                    DatePicker("", selection: $beforeDate, in: ...Date(), displayedComponents: .date)
                        .datePickerStyle(.field).labelsHidden().fixedSize()
                    Spacer(minLength: 0)
                }
                HStack(spacing: 9) {
                    Image(systemName: "checkmark.shield").font(.system(size: 11)).foregroundStyle(Paper.clear)
                    Text("Starred, flagged, and live sign/pay/legal mail is always kept.")
                        .font(.system(size: 11)).foregroundStyle(Paper.ink4)
                        .fixedSize(horizontal: false, vertical: true)
                    Spacer(minLength: 0)
                }
            }
            .padding(16).glassSurface(13).frame(maxWidth: 340).padding(.top, 20)

            Spacer(minLength: 18)

            Button {
                m.archiveBefore(before: Self.apiFmt.string(from: beforeDate))
                m.dismissBacklog()
            } label: {
                HStack(spacing: 7) {
                    Image(systemName: "archivebox").font(.system(size: 12, weight: .bold))
                    Text("Archive before \(Self.humanFmt.string(from: beforeDate))")
                }
            }
            .buttonStyle(PrimaryButtonStyle(enabled: !m.isBusy)).disabled(m.isBusy)

            Button("Skip for now") { m.dismissBacklog() }
                .buttonStyle(.plain).font(.system(size: 12, weight: .medium))
                .foregroundStyle(Paper.ink3).padding(.top, 12)

            Spacer(minLength: 24)
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// Onboarding credential setup: the user creates a free Desktop OAuth client in
// Google Cloud Console and pastes the downloaded client_secret.json here, so a
// stranger can set zero up without hand-editing files. The sign-in consent still
// happens in the browser when they connect. The JSON stays on this Mac.
private struct CredentialsCard: View {
    @EnvironmentObject var m: KeeperModel
    @State private var pasted = ""
    @State private var claudeCopied = false

    // The Google Cloud OAuth step is the one real wall in setup. "Set it up with
    // Claude" copies this prompt; the user pastes it into Claude Code (which most zero
    // users already have) and Claude drives the console with them. Self-contained so a
    // fresh Claude session has everything it needs. The "In production" step is spelled
    // out because skipping it silently breaks sync after 7 days.
    private static let claudePrompt = """
    I'm setting up "zero", a macOS menu-bar app that triages my Gmail. It needs its own \
    free Google OAuth client (a Google Cloud app I own) so it can sign in to my inboxes. \
    Please set this up with me, end to end.

    Do it in my browser — use browser automation if you have it; otherwise give me one \
    click at a time and wait for me. Steps:
    1. Open https://console.cloud.google.com and create a project named "zero" (or reuse one).
    2. Enable the Gmail API for that project.
    3. In "Google Auth Platform", configure the consent screen: External user type, app \
    name "zero", my own email as the support and developer contact.
    4. CRITICAL: on the Audience tab, set Publishing status to "In production". In \
    "Testing" status Google expires access after 7 days and zero silently stops syncing.
    5. Go to Clients → Create client → Application type "Desktop app" → create, then \
    download the client JSON.
    6. Show me the full contents of that downloaded JSON so I can paste it into zero's \
    "Set up Google access" box. It stays on my Mac.

    Stop if Google asks for app verification — it isn't required for personal use. Walk \
    me through anything you can't click yourself.
    """

    private func copyClaudePrompt() {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(Self.claudePrompt, forType: .string)
        withAnimation(Motion.pop) { claudeCopied = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            withAnimation(Motion.pop) { claudeCopied = false }
        }
    }

    private var pasteReady: Bool { !pasted.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("CONNECT GOOGLE").font(.system(size: 10, weight: .semibold)).kerning(0.6)
                .foregroundStyle(Paper.ink4)
            Text("zero signs in through your own free Google app. You create it once; it stays on this Mac.")
                .font(.system(size: 12.5)).foregroundStyle(Paper.ink2)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 7)

            // Fastest path, led with on purpose: hand the whole console dance to Claude.
            Button { copyClaudePrompt() } label: {
                HStack(spacing: 10) {
                    Image(systemName: claudeCopied ? "checkmark.circle.fill" : "sparkles")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(claudeCopied ? Paper.clear : Paper.accentSoft)
                    VStack(alignment: .leading, spacing: 1) {
                        Text(claudeCopied ? "Copied. Paste into Claude Code." : "Set it up with Claude")
                            .font(.system(size: 12.5, weight: .semibold)).foregroundStyle(Paper.ink)
                        Text(claudeCopied ? "Claude takes it from here." : "It opens the console and does it with you.")
                            .font(.system(size: 10.5)).foregroundStyle(Paper.ink3)
                    }
                    Spacer(minLength: 0)
                    if !claudeCopied {
                        Image(systemName: "doc.on.clipboard").font(.system(size: 11)).foregroundStyle(Paper.ink4)
                    }
                }
                .padding(.vertical, 10).padding(.horizontal, 12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .glassSurface(11, tint: Paper.accent.opacity(0.14))
                .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous)
                    .strokeBorder(Paper.accent.opacity(0.30), lineWidth: 0.75))
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .padding(.top, 13)

            // Divider into the manual route.
            HStack(spacing: 10) {
                Rectangle().fill(Paper.hairline.opacity(0.10)).frame(height: 0.5)
                Text("or set it up yourself").font(.system(size: 10, weight: .medium))
                    .foregroundStyle(Paper.ink4).fixedSize()
                Rectangle().fill(Paper.hairline.opacity(0.10)).frame(height: 0.5)
            }
            .padding(.top, 14)

            Link(destination: URL(string: "https://console.cloud.google.com/auth/clients")!) {
                HStack(spacing: 5) {
                    Image(systemName: "arrow.up.forward.square")
                    Text("Open Google Cloud Console")
                }.font(.system(size: 11.5, weight: .medium)).foregroundStyle(Paper.accentSoft)
            }.buttonStyle(.plain)
            .padding(.top, 12)

            VStack(alignment: .leading, spacing: 9) {
                StepRow(n: 1, text: "Enable the Gmail API for a new project.")
                StepRow(n: 2, text: "Create an OAuth client, type Desktop app.")
                StepRow(n: 3, text: "Set Publishing status to In production.",
                        warn: "In Testing, Google cuts access after 7 days.")
                StepRow(n: 4, text: "Download the JSON, then paste it below.")
            }
            .padding(.top, 11)

            ZStack(alignment: .topLeading) {
                TextEditor(text: $pasted)
                    .font(.system(size: 11, design: .monospaced))
                    .scrollContentBackground(.hidden)
                    .frame(height: 58).padding(8).glassSurface(8)
                if pasted.isEmpty {
                    Text("Paste client_secret.json here")
                        .font(.system(size: 11)).foregroundStyle(Paper.ink4)
                        .padding(.horizontal, 13).padding(.vertical, 16).allowsHitTesting(false)
                }
            }
            .padding(.top, 12)

            Button { m.saveCredentials(pasted) } label: {
                Text("Save Google access").frame(maxWidth: .infinity)
            }
            .buttonStyle(PrimaryButtonStyle(enabled: pasteReady))
            .disabled(!pasteReady)
            .padding(.top, 9)

            HStack(spacing: 0) {
                Link(destination: URL(string: "https://github.com/drewling/zero/blob/master/docs/SETUP.md")!) {
                    HStack(spacing: 4) {
                        Text("Guided walkthrough")
                        Image(systemName: "arrow.up.forward")
                    }.font(.system(size: 11, weight: .medium)).foregroundStyle(Paper.accentSoft)
                }.buttonStyle(.plain)
                Spacer(minLength: 0)
            }
            .padding(.top, 13)

            Text("Sign-in opens in your browser; the app never sees your password.")
                .font(.system(size: 10)).foregroundStyle(Paper.ink4)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, 7)
        }
        .padding(16).glassSurface(13).frame(maxWidth: 320).padding(.top, 14)
    }
}

// A numbered manual-setup step: badge + concise instruction, with an optional warning
// line for the load-bearing detail (the "In production" gotcha that silently kills sync).
private struct StepRow: View {
    let n: Int
    let text: String
    var warn: String? = nil
    var body: some View {
        HStack(alignment: .top, spacing: 9) {
            Text("\(n)")
                .font(.system(size: 10, weight: .bold)).foregroundStyle(Paper.ink2)
                .frame(width: 18, height: 18)
                .background(Circle().fill(Paper.raised.opacity(0.10)))
                .overlay(Circle().strokeBorder(Paper.hairline.opacity(0.14), lineWidth: 0.5))
            VStack(alignment: .leading, spacing: 2) {
                Text(text).font(.system(size: 11.5)).foregroundStyle(Paper.ink2)
                    .fixedSize(horizontal: false, vertical: true)
                if let warn {
                    Text(warn).font(.system(size: 10)).foregroundStyle(Paper.danger.opacity(0.92))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            Spacer(minLength: 0)
        }
    }
}

private struct TrustRow: View {
    let symbol: String; let text: String
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: symbol).font(.system(size: 12, weight: .semibold))
                .foregroundStyle(Paper.accentSoft).frame(width: 18)
            Text(text).font(.system(size: 12)).foregroundStyle(Paper.ink2)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

private struct ToolRow: View {
    let name: String; let cmd: String
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "arrow.down.circle").font(.system(size: 12)).foregroundStyle(Paper.danger)
            VStack(alignment: .leading, spacing: 2) {
                Text(name).font(.system(size: 12, weight: .medium))
                Text(cmd).font(.system(size: 11, design: .monospaced)).foregroundStyle(Paper.ink3)
                    .textSelection(.enabled)
            }
            Spacer(minLength: 0)
        }
    }
}
