// Updater.swift — zero's self-updater. Checks GitHub releases for a newer version,
// surfaces it in-app + via a notification, and (on one click) downloads the DMG and
// hands off to a tiny detached helper that waits for this app to quit, swaps the
// bundle in place, strips quarantine, and relaunches. Same mechanics install-zero.sh
// already proves — no Sparkle, no new dependency, no notarization needed.
//
// Stored @Published flags live on KeeperModel (see "Auto-update" block there); the
// logic is here as an extension to keep the model file's diff small.

import SwiftUI
import AppKit

extension KeeperModel {
    static let repoSlug = "drewling/zero"

    var currentVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0"
    }

    func setAutoCheckUpdates(_ on: Bool) {
        autoCheckUpdates = on
        UserDefaults.standard.set(on, forKey: "autoCheckUpdates")
        if on && updateAvailable == nil { Task { await checkForUpdates(manual: false) } }
    }

    /// Launch entry point: announce a just-applied update, then check now and every few
    /// hours while resident. The loop always runs; each pass is gated on the toggle, so
    /// flipping auto-check on mid-session resumes checking without a relaunch.
    func startUpdateWatch() {
        announceIfUpdated()
        Task {
            while !Task.isCancelled {
                if autoCheckUpdates { await checkForUpdates(manual: false) }
                try? await Task.sleep(nanoseconds: 6 * 3_600 * 1_000_000_000)   // 6h
            }
        }
    }

    /// Ask GitHub for the latest release. `manual` surfaces success/failure toasts;
    /// the background check stays silent except for the "update available" banner +
    /// a single notification per new version.
    func checkForUpdates(manual: Bool) async {
        if checkingForUpdates { return }
        checkingForUpdates = true
        defer { checkingForUpdates = false }

        guard let url = URL(string: "https://api.github.com/repos/\(Self.repoSlug)/releases/latest") else { return }
        var req = URLRequest(url: url, timeoutInterval: 12)
        req.setValue("zero-updater", forHTTPHeaderField: "User-Agent")          // GitHub rejects UA-less calls
        req.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        do {
            let (data, resp) = try await URLSession.shared.data(for: req)
            guard (resp as? HTTPURLResponse)?.statusCode == 200 else {
                if manual { toast("Couldn't reach the update server") }
                return
            }
            let release = try JSONDecoder().decode(GithubRelease.self, from: data)
            lastUpdateCheck = Date()   // stamp only on a successful check, not on failures
            if versionIsNewer(release.version, than: currentVersion) {
                let isNewlySeen = updateAvailable?.version != release.version
                updateAvailable = release
                if isNewlySeen { RunNotifier.postUpdateAvailable(version: release.version, url: release.htmlURL) }
            } else {
                updateAvailable = nil
                if manual { toast("You're on the latest version (\(currentVersion))") }
            }
        } catch {
            if manual { toast("Couldn't check for updates") }
        }
    }

    /// Download the latest DMG, then spawn the detached helper and quit so it can
    /// swap the bundle and relaunch us on the new version.
    func installUpdate() {
        guard let release = updateAvailable, !installingUpdate else { return }
        installingUpdate = true
        guard let dmgURL = URL(string: "https://github.com/\(Self.repoSlug)/releases/latest/download/zero.dmg") else {
            installingUpdate = false; return
        }
        Task {
            do {
                let (tmp, _) = try await URLSession.shared.download(from: dmgURL)
                // download(from:) gives an extension-less temp name; rename to .dmg so
                // hdiutil is happy.
                let dmg = tmp.deletingLastPathComponent().appendingPathComponent("zero-\(release.version).dmg")
                try? FileManager.default.removeItem(at: dmg)
                try FileManager.default.moveItem(at: tmp, to: dmg)
                // Record where we came from so the next launch can say "updated to X".
                UserDefaults.standard.set(currentVersion, forKey: "preUpdateVersion")
                try launchUpdaterHelper(dmgPath: dmg.path)
                NSApp.terminate(nil)
            } catch {
                installingUpdate = false
                UserDefaults.standard.removeObject(forKey: "preUpdateVersion")
                toast("Update failed to download")
            }
        }
    }

    /// Write and run a detached bash helper. It outlives this app (children aren't
    /// killed when the parent exits), waits for the old process to die, swaps the
    /// bundle from the DMG, de-quarantines, and reopens zero.
    private func launchUpdaterHelper(dmgPath: String) throws {
        let dest = Bundle.main.bundlePath                 // wherever zero.app actually lives
        let pid = ProcessInfo.processInfo.processIdentifier
        // Stage the full copy beside the install first, then rm+mv — so a partial/failed
        // copy can never leave the user with no app. mv on the same volume is atomic.
        // Every failure path reopens the existing app so the user is never left with none.
        // On any failure: drop a breadcrumb and reopen the existing app, so the next
        // launch can tell the user the update didn't apply (instead of a failed update
        // silently masquerading as success). Success removes the breadcrumb.
        let script = """
        #!/bin/bash
        # zero self-update helper (generated). Swap the bundle once the old app quits.
        DEST=\(shellQuote(dest)); DMG=\(shellQuote(dmgPath)); APP_PID=\(pid)
        STAGE="$(dirname "$DEST")/.zero-update-stage.app"
        FAILED="$(dirname "$DEST")/.zero-update-failed"
        fail() { echo "$1" > "$FAILED" 2>/dev/null; /usr/bin/open "$DEST"; exit 1; }
        for _ in $(seq 1 60); do kill -0 "$APP_PID" 2>/dev/null || break; sleep 0.25; done
        # Never swap a still-running app (terminate could be deferred/cancelled): bail.
        if kill -0 "$APP_PID" 2>/dev/null; then fail "app did not quit"; fi
        MNT="$(hdiutil attach "$DMG" -nobrowse -readonly -mountrandom /tmp 2>/dev/null | grep -Eo '/tmp/[^[:space:]]+' | tail -1)"
        if [ -z "$MNT" ] || [ ! -d "$MNT/zero.app" ]; then fail "could not mount $DMG"; fi
        rm -rf "$STAGE"
        if ! /usr/bin/ditto "$MNT/zero.app" "$STAGE"; then
          /usr/bin/hdiutil detach "$MNT" -quiet 2>/dev/null || true; fail "could not copy zero.app"
        fi
        /usr/bin/hdiutil detach "$MNT" -quiet 2>/dev/null || true
        rm -rf "$DEST" && mv "$STAGE" "$DEST" || fail "could not replace $DEST"
        # De-quarantine like install-zero.sh: -dr, then -cr fallback. A stray PATH `xattr`
        # that ignores -r would silently no-op and leave the ad-hoc app Gatekeeper-blocked.
        /usr/bin/xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || /usr/bin/xattr -cr "$DEST" 2>/dev/null || true
        rm -f "$DMG" "$FAILED"
        /usr/bin/open "$DEST"
        """
        let scriptURL = FileManager.default.temporaryDirectory.appendingPathComponent("zero-update.sh")
        try script.write(to: scriptURL, atomically: true, encoding: .utf8)
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/bin/bash")
        p.arguments = [scriptURL.path]
        try p.run()
    }

    /// If a prior run set preUpdateVersion: a newer build now means the swap succeeded
    /// (notify "updated"); same version + a failure breadcrumb means it didn't apply
    /// (tell the user, so a failed update never masquerades as success).
    private func announceIfUpdated() {
        let dir = (Bundle.main.bundlePath as NSString).deletingLastPathComponent
        let marker = dir + "/.zero-update-failed"
        let key = "preUpdateVersion"
        guard let prev = UserDefaults.standard.string(forKey: key) else { return }
        UserDefaults.standard.removeObject(forKey: key)
        if versionIsNewer(currentVersion, than: prev) {
            try? FileManager.default.removeItem(atPath: marker)
            let url = "https://github.com/\(Self.repoSlug)/releases/tag/v\(currentVersion)"
            RunNotifier.postUpdated(version: currentVersion, url: url)
        } else if FileManager.default.fileExists(atPath: marker) {
            try? FileManager.default.removeItem(atPath: marker)
            RunNotifier.post(title: "Update didn't apply",
                             body: "zero is still on \(currentVersion). Open zero and try again from Settings ▸ Updates.")
        }
    }

    private func shellQuote(_ s: String) -> String {
        "'" + s.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}
