// inbox-keeper — macOS menu-bar shell.
//
// Lives in the menu bar (no Dock icon). Shows the web panel in a borderless
// floating window we draw ourselves: an opaque paper bubble with a paper arrow
// pointing up at the menu-bar item. Drawing it ourselves (rather than NSPopover)
// gives full control of the arrow colour and the corner radius, with no system
// vibrancy material that we can't tint. The content is opaque so it can never
// render blank. Starts the local panel server on launch, kills it on quit.

import AppKit
import WebKit

let PORT = ProcessInfo.processInfo.environment["KEEPER_PORT"] ?? "8765"
let PANEL_URL = URL(string: "http://127.0.0.1:\(PORT)/?app=1")!
let PANEL_W: CGFloat = 420
let PANEL_H: CGFloat = 640
let ARROW_H: CGFloat = 9
let ARROW_W: CGFloat = 22
let CORNER: CGFloat = 13
let GAP: CGFloat = 1            // arrow tip to the menu bar
// Matches CSS --paper: oklch(98.6% 0.006 75).
let PAPER = NSColor(srgbRed: 0.974, green: 0.957, blue: 0.930, alpha: 1)
let HAIRLINE = NSColor(srgbRed: 0.88, green: 0.866, blue: 0.84, alpha: 1)

func resolveRepoRoot() -> String? {
    let fm = FileManager.default
    if let env = ProcessInfo.processInfo.environment["MAIL_TRIAGE_DIR"],
       fm.fileExists(atPath: "\(env)/lib/keeper_server.py") { return env }
    let home = fm.homeDirectoryForCurrentUser.path
    let guess = "\(home)/mail-triage"
    if fm.fileExists(atPath: "\(guess)/lib/keeper_server.py") { return guess }
    var dir = URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent()
    for _ in 0..<6 {
        if fm.fileExists(atPath: dir.appendingPathComponent("lib/keeper_server.py").path) {
            return dir.path
        }
        dir = dir.deletingLastPathComponent()
    }
    return nil
}

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

// The paper bubble + upward arrow. Drawn (not layer-filled) so the window shadow
// follows the bubble silhouette including the arrow.
final class BubbleView: NSView {
    var arrowX: CGFloat = PANEL_W - 40 { didSet { needsDisplay = true } }

    private func bubblePath() -> NSBezierPath {
        let bodyTop = bounds.height - ARROW_H
        let body = NSRect(x: 0, y: 0, width: bounds.width, height: bodyTop)
        let path = NSBezierPath(roundedRect: body, xRadius: CORNER, yRadius: CORNER)
        let tri = NSBezierPath()
        tri.move(to: NSPoint(x: arrowX - ARROW_W / 2, y: bodyTop - 0.5))
        tri.line(to: NSPoint(x: arrowX, y: bounds.height))
        tri.line(to: NSPoint(x: arrowX + ARROW_W / 2, y: bodyTop - 0.5))
        tri.close()
        path.append(tri)
        return path
    }

    override func draw(_ dirtyRect: NSRect) {
        let path = bubblePath()
        PAPER.setFill()
        path.fill()
        HAIRLINE.setStroke()
        path.lineWidth = 0.5
        path.stroke()
    }
}

final class KeyablePanel: NSPanel {
    override var canBecomeKey: Bool { true }
}

final class AppController: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate {
    let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    var panel: KeyablePanel!
    var bubble: BubbleView!
    var server: Process?
    var webView: WKWebView!
    var loadRetries = 0
    var repoMissing = false
    var clickMonitor: Any?
    var escMonitor: Any?

    func applicationDidFinishLaunching(_ note: Notification) {
        NSApp.setActivationPolicy(.accessory)
        startServer()
        setupStatusItem()
        setupPanel()
    }

    func setupStatusItem() {
        if let button = statusItem.button {
            let img = NSImage(systemSymbolName: "tray.full", accessibilityDescription: "inbox-keeper")
            img?.isTemplate = true
            button.image = img
            button.action = #selector(togglePanel)
            button.target = self
        }
    }

    func setupPanel() {
        let total = NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H + ARROW_H)
        bubble = BubbleView(frame: total)

        let cfg = WKWebViewConfiguration()
        webView = WKWebView(frame: NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H),
                            configuration: cfg)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.wantsLayer = true
        webView.layer?.cornerRadius = CORNER
        webView.layer?.masksToBounds = true
        webView.setValue(true, forKey: "drawsBackground")   // opaque paper — never blank
        bubble.addSubview(webView)

        panel = KeyablePanel(contentRect: total,
                             styleMask: [.borderless, .nonactivatingPanel],
                             backing: .buffered, defer: false)
        panel.isFloatingPanel = true
        panel.level = .popUpMenu
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = true
        panel.isMovableByWindowBackground = false
        panel.hidesOnDeactivate = false
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.contentView = bubble

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
        <style>html,body{height:100%}body{font:14px -apple-system,system-ui;color:#3a342e;
        background:#f8f4ed;margin:0;display:flex;align-items:center;justify-content:center;text-align:center}
        .b{max-width:300px;padding:24px}h2{font-size:17px;margin:0 0 8px}p{color:#7a7268;line-height:1.5}
        code{background:#ece6dc;padding:2px 5px;border-radius:4px;font-size:12px}</style></head>
        <body><div class="b"><h2>\(title)</h2><p>\(detail)</p></div></body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
    }

    func webView(_ wv: WKWebView, didFailProvisionalNavigation nav: WKNavigation!, withError e: Error) {
        guard loadRetries < 25 else {
            showError("Couldn’t reach the panel",
                      "The local keeper server didn’t respond on port \(PORT). Try quitting and reopening, or run <code>./bin/inbox-keeper dashboard</code> from the repo.")
            return
        }
        loadRetries += 1
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { [weak self] in self?.loadPanel() }
    }

    // Open external links (a tapped open-loop -> Gmail) in the user's real browser.
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

    func webView(_ wv: WKWebView, createWebViewWith config: WKWebViewConfiguration,
                 for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = action.request.url { NSWorkspace.shared.open(url) }
        return nil
    }

    @objc func togglePanel() {
        if panel.isVisible { hidePanel() } else { showPanel() }
    }

    func showPanel() {
        positionPanel()
        webView.reload()
        panel.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        clickMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) {
            [weak self] _ in
            guard let self = self else { return }
            if let button = self.statusItem.button, let bWin = button.window {
                let f = bWin.convertToScreen(button.convert(button.bounds, to: nil))
                if f.contains(NSEvent.mouseLocation) { return }  // toggle handles the item click
            }
            self.hidePanel()
        }
        escMonitor = NSEvent.addLocalMonitorForEvents(matching: .keyDown) { [weak self] e in
            if e.keyCode == 53 { self?.hidePanel(); return nil }
            return e
        }
    }

    func hidePanel() {
        panel.orderOut(nil)
        if let m = clickMonitor { NSEvent.removeMonitor(m); clickMonitor = nil }
        if let m = escMonitor { NSEvent.removeMonitor(m); escMonitor = nil }
    }

    // Snug under the menu-bar item: arrow tip just below the bar, pointing at the
    // item's centre; window clamped to the screen.
    func positionPanel() {
        guard let button = statusItem.button, let bWin = button.window else { return }
        let f = bWin.convertToScreen(button.convert(button.bounds, to: nil))
        let visible = (bWin.screen ?? NSScreen.main)?.visibleFrame
            ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let winH = PANEL_H + ARROW_H
        // Place the window so the arrow sits ~40px from its right edge under the item.
        var originX = f.midX - (PANEL_W - 40)
        originX = max(visible.minX + 8, min(originX, visible.maxX - PANEL_W - 8))
        let originY = f.minY - GAP - winH
        var ax = f.midX - originX
        ax = max(CORNER + ARROW_W, min(ax, PANEL_W - CORNER - ARROW_W))
        bubble.arrowX = ax
        bubble.needsDisplay = true
        panel.setFrame(NSRect(x: originX, y: originY, width: PANEL_W, height: winH), display: true)
    }

    func startServer() {
        guard let root = resolveRepoRoot() else {
            repoMissing = true
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
