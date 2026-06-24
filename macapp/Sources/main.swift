// inbox-keeper — macOS menu-bar shell.
//
// Lives in the menu bar (no Dock icon). On launch it starts the local panel
// server (lib/keeper_server.py) and shows the web panel in a popover anchored to
// the menu-bar item. Quitting terminates the server. The shell is deliberately
// thin: all UI is the web panel, all logic is the Python the rest of the repo
// already uses.

import AppKit
import WebKit

let PORT = ProcessInfo.processInfo.environment["KEEPER_PORT"] ?? "8765"
let PANEL_URL = URL(string: "http://127.0.0.1:\(PORT)/")!

// Resolve the repo root: explicit env, then ~/mail-triage, then the app's own
// enclosing folder (supports running the app from inside a clone).
func resolveRepoRoot() -> String? {
    let fm = FileManager.default
    if let env = ProcessInfo.processInfo.environment["MAIL_TRIAGE_DIR"],
       fm.fileExists(atPath: "\(env)/lib/keeper_server.py") { return env }
    let home = fm.homeDirectoryForCurrentUser.path
    let guess = "\(home)/mail-triage"
    if fm.fileExists(atPath: "\(guess)/lib/keeper_server.py") { return guess }
    // Walk up from the executable (…/inbox-keeper.app/Contents/MacOS/…).
    var dir = URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent()
    for _ in 0..<6 {
        if fm.fileExists(atPath: dir.appendingPathComponent("lib/keeper_server.py").path) {
            return dir.path
        }
        dir = dir.deletingLastPathComponent()
    }
    return nil
}

// A generous PATH so a Finder-launched app can still find gws / node / python,
// mirroring config.sh (launchd & Finder give a minimal PATH otherwise).
func augmentedPath() -> String {
    let home = FileManager.default.homeDirectoryForCurrentUser.path
    var parts = ["/opt/homebrew/bin", "/opt/homebrew/anaconda3/bin", "/usr/local/bin",
                 "\(home)/.local/bin", "/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    let nvm = "\(home)/.nvm/versions/node"
    if let entries = try? FileManager.default.contentsOfDirectory(atPath: nvm) {
        for e in entries.sorted().reversed() { parts.insert("\(nvm)/\(e)/bin", at: 0) }
    }
    if let existing = ProcessInfo.processInfo.environment["PATH"] { parts.append(existing) }
    return parts.joined(separator: ":")
}

final class AppController: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate {
    let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    let popover = NSPopover()
    var server: Process?
    var webView: WKWebView!
    var loadRetries = 0
    var repoMissing = false

    func applicationDidFinishLaunching(_ note: Notification) {
        NSApp.setActivationPolicy(.accessory)
        startServer()
        setupStatusItem()
        setupPopover()
    }

    func setupStatusItem() {
        if let button = statusItem.button {
            let img = NSImage(systemSymbolName: "tray.full", accessibilityDescription: "inbox-keeper")
            img?.isTemplate = true
            button.image = img
            button.action = #selector(togglePopover)
            button.target = self
        }
    }

    func setupPopover() {
        let cfg = WKWebViewConfiguration()
        webView = WKWebView(frame: NSRect(x: 0, y: 0, width: 420, height: 640), configuration: cfg)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.setValue(false, forKey: "drawsBackground")  // transparent so panel radius shows
        let vc = NSViewController()
        vc.view = webView
        popover.contentViewController = vc
        popover.contentSize = NSSize(width: 420, height: 640)
        popover.behavior = .transient
        popover.animates = true
        if repoMissing {
            showError("Can’t find the inbox-keeper folder",
                      "Set <code>MAIL_TRIAGE_DIR</code> to your clone, or put it at <code>~/mail-triage</code>. Looked for <code>lib/keeper_server.py</code>.")
        } else {
            loadPanel()
        }
    }

    func loadPanel() { webView.load(URLRequest(url: PANEL_URL)) }

    func showError(_ title: String, _ detail: String) {
        let html = """
        <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>body{font:14px -apple-system,system-ui;color:#3a342e;background:#f7f3ec;
        margin:0;height:100vh;display:flex;align-items:center;justify-content:center;text-align:center}
        .b{max-width:300px;padding:24px}h2{font-size:17px;margin:0 0 8px}p{color:#7a7268;line-height:1.5}
        code{background:#ece6dc;padding:2px 5px;border-radius:4px;font-size:12px}</style></head>
        <body><div class="b"><h2>\(title)</h2><p>\(detail)</p></div></body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    // The server may not be listening the instant the webview loads; retry briefly,
    // then surface the failure instead of leaving a blank popover.
    func webView(_ wv: WKWebView, didFailProvisionalNavigation nav: WKNavigation!, withError e: Error) {
        guard loadRetries < 25 else {
            showError("Couldn’t reach the panel",
                      "The local keeper server didn’t respond on port \(PORT). Try quitting and reopening, or run <code>./bin/inbox-keeper dashboard</code> from the repo.")
            return
        }
        loadRetries += 1
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { [weak self] in self?.loadPanel() }
    }

    // Open external links (a tapped open-loop -> Gmail) in the user's real browser,
    // never inside the popover. Localhost stays in-panel.
    func webView(_ wv: WKWebView, decidePolicyFor action: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let url = action.request.url, let host = url.host,
           host != "127.0.0.1", host != "localhost" {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    // window.open(..., "_blank") from the panel -> open externally, return no new view.
    func webView(_ wv: WKWebView, createWebViewWith config: WKWebViewConfiguration,
                 for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = action.request.url { NSWorkspace.shared.open(url) }
        return nil
    }

    @objc func togglePopover() {
        guard let button = statusItem.button else { return }
        if popover.isShown { popover.performClose(nil) }
        else {
            popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
            popover.contentViewController?.view.window?.makeKey()
            webView.reload()
        }
    }

    func startServer() {
        guard let root = resolveRepoRoot() else {
            repoMissing = true   // surfaced as an error page in setupPopover()
            return
        }
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        p.arguments = ["python3", "\(root)/lib/keeper_server.py"]
        var env = ProcessInfo.processInfo.environment
        env["PATH"] = augmentedPath()
        env["GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND"] = "file"
        env["KEEPER_PORT"] = PORT
        env["MAIL_TRIAGE_DIR"] = root
        p.environment = env
        p.currentDirectoryURL = URL(fileURLWithPath: root)
        do {
            try p.run()
            server = p
        } catch {
            // Don't fail silently: the webview retry will time out and show an error,
            // but make the cause explicit on the next runloop tick.
            DispatchQueue.main.async { [weak self] in
                self?.showError("Couldn’t start the keeper server",
                                "Failed to launch python3: \(error.localizedDescription). Make sure Python 3 is installed.")
            }
        }
    }

    func applicationWillTerminate(_ note: Notification) {
        server?.terminate()
    }
}

let app = NSApplication.shared
let controller = AppController()
app.delegate = controller
app.run()
