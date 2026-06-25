// zero — macOS menu-bar app.
//
// Lives in the menu bar (no Dock icon). The panel is fully native SwiftUI hosted
// inside a real macOS 26 "Liquid Glass" surface (NSGlassEffectView) — not a web
// view, and not a hand-painted bitmap. The AppKit shell owns the status item, the
// borderless floating panel, and the local keeper server's lifecycle. A single
// long-lived KeeperModel backs the UI, so closing and reopening the panel never
// loses an in-progress run: it re-attaches to the live server-side job on open.

import AppKit
import SwiftUI
import UserNotifications

let PORT = ProcessInfo.processInfo.environment["KEEPER_PORT"] ?? "8765"
let PANEL_W: CGFloat = 420
let PANEL_H: CGFloat = 640
let CORNER: CGFloat = 17        // menu-surface corner radius
let ARROW_W: CGFloat = 44       // arrow base width (wide raised-cosine ogee = gentle, smooth join)
let ARROW_H: CGFloat = 11       // how far the arrow tip protrudes above the body
let ARROW_CLAMP: CGFloat = 42   // keep the arrow (incl. its wide base) off the rounded top corners
let GAP: CGFloat = 5            // arrow tip to the menu bar

func resolveRepoRoot() -> String? {
    let fm = FileManager.default
    // Dev opt-in: run straight from a source checkout when explicitly pointed at one.
    if let env = ProcessInfo.processInfo.environment["MAIL_TRIAGE_DIR"],
       fm.fileExists(atPath: "\(env)/lib/keeper_server.py") { return env }
    // A packaged app must NOT auto-grab a source checkout by guessing home-dir paths:
    // that path may be inside ~/Documents, which macOS TCC blocks for the app's helper
    // processes (and the daily LaunchAgent). We only use a source tree when the binary
    // is being run from *inside* one (walk up from the executable — the dev build case);
    // otherwise we seed the bundle into Application Support (not TCC-protected) and run
    // from there. That makes a downloaded .dmg behave identically for every user.
    var dir = URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent()
    for _ in 0..<6 {
        if fm.fileExists(atPath: dir.appendingPathComponent("lib/keeper_server.py").path) {
            // Don't auto-run from a source checkout that lives inside a TCC-protected
            // folder (~/Documents, ~/Desktop, ~/Downloads). The server reads and writes
            // repo files (logs, state, learning, drafts) on every launch and on the
            // daily LaunchAgent run — doing that inside ~/Documents triggers the macOS
            // "zero would like to access your Documents folder" prompt every time.
            // Seed into Application Support instead (not TCC-protected). A dev who wants
            // live source from such a location can still force it via MAIL_TRIAGE_DIR.
            if isInTCCProtectedDir(dir.path) { break }
            return dir.path
        }
        dir = dir.deletingLastPathComponent()
    }
    // Packaged .app (or a checkout inside a protected folder): seed the bundled
    // runtime into a writable support dir and run from there.
    return seedFromBundle()
}

/// True if `path` is inside one of the macOS TCC-gated home folders, where any
/// file access pops the per-folder privacy prompt.
private func isInTCCProtectedDir(_ path: String) -> Bool {
    let home = FileManager.default.homeDirectoryForCurrentUser.path
    let protected = ["\(home)/Documents", "\(home)/Desktop", "\(home)/Downloads"]
    let p = URL(fileURLWithPath: path).standardized.path
    return protected.contains { p == $0 || p.hasPrefix($0 + "/") }
}

/// Application Support location the packaged app runs from. The code lives in the
/// bundle (read-only, replaced on update); the running copy + all user data live
/// here so updates never clobber accounts, policy, learning, or state.
func supportDirURL() -> URL {
    FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("Library/Application Support/zero", isDirectory: true)
}

/// First run = no connected account yet. accounts.json is written only after the
/// user connects an inbox; seedFromBundle never creates it (only the .example). Read
/// the file directly so we can decide at launch, before the server is up.
func hasConnectedAccount() -> Bool {
    let url = supportDirURL().appendingPathComponent("accounts.json")
    guard let data = try? Data(contentsOf: url),
          let arr = try? JSONSerialization.jsonObject(with: data) as? [Any] else { return false }
    return !arr.isEmpty
}

/// Copy the bundled `Contents/Resources/payload` into the support dir. Pure code is
/// refreshed every launch (so updates apply); user-editable files are seeded only
/// when missing; user data (accounts, learning, drafts, logs, state) is never touched.
private func seedFromBundle() -> String? {
    let fm = FileManager.default
    guard let res = Bundle.main.resourceURL else { return nil }
    let payload = res.appendingPathComponent("payload", isDirectory: true)
    guard fm.fileExists(atPath: payload.appendingPathComponent("lib/keeper_server.py").path) else { return nil }
    let support = supportDirURL()
    // One-time migration from the pre-rename support dir, so existing users keep
    // their accounts, policy, learning, and state across the inbox-keeper→zero rename.
    let legacy = fm.homeDirectoryForCurrentUser
        .appendingPathComponent("Library/Application Support/inbox-keeper", isDirectory: true)
    if !fm.fileExists(atPath: support.path), fm.fileExists(atPath: legacy.path) {
        try? fm.moveItem(at: legacy, to: support)
    }
    try? fm.createDirectory(at: support, withIntermediateDirectories: true)

    func overwrite(_ rel: String) {
        let src = payload.appendingPathComponent(rel), dst = support.appendingPathComponent(rel)
        guard fm.fileExists(atPath: src.path) else { return }
        try? fm.createDirectory(at: dst.deletingLastPathComponent(), withIntermediateDirectories: true)
        try? fm.removeItem(at: dst)
        try? fm.copyItem(at: src, to: dst)
    }
    func seedIfMissing(_ rel: String) {
        let dst = support.appendingPathComponent(rel)
        guard !fm.fileExists(atPath: dst.path) else { return }
        let src = payload.appendingPathComponent(rel)
        guard fm.fileExists(atPath: src.path) else { return }
        try? fm.copyItem(at: src, to: dst)
    }
    // Code + templates — safe to refresh (never user data). knowledge: only the template.
    ["lib", "bin", "config.py", "config.sh",
     "accounts.json.example", "knowledge/profile.example.md"].forEach(overwrite)
    // User-editable — seed once, then leave their edits alone.
    ["keep-policy.md", "categories.json"].forEach(seedIfMissing)

    return fm.fileExists(atPath: support.appendingPathComponent("lib/keeper_server.py").path)
        ? support.path : nil
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

final class KeyablePanel: NSPanel {
    override var canBecomeKey: Bool { true }
}

/// Dark frosted surface for the panel — classic vibrancy (what Raycast-style panels
/// use), masked to a rounded body + upward arrow. Unlike NSGlassEffectView this has
/// no bright specular rim, so there's no hairline outline around the window.
///
/// SEAM FIX: The beak shares the same mask + vibrancy as the body, but the SwiftUI
/// graphite gradient overlay (in PanelView) only covers the body rect. Without a
/// matching tint the beak shows as raw hudWindow vibrancy — lighter and distinctly
/// different from the dark header just below it. We paint a matching graphite gradient
/// CAGradientLayer directly over the beak region so the beak reads as one continuous
/// surface with the header. The body gradient is intentionally excluded (the SwiftUI
/// layer covers that area) so we don't double-tint the body.
final class GlassSurface: NSView {
    let effect = NSVisualEffectView()
    var arrowX: CGFloat = PANEL_W - 40 { didSet { if oldValue != arrowX { applyMask(); updateBeakGradient() } } }

    // ponytail: CAGradientLayer is cheap; one gradient over the beak-only region.
    private let beakGradient = CAGradientLayer()

    override init(frame: NSRect) {
        super.init(frame: frame)
        wantsLayer = true
        effect.material = .hudWindow            // dark, translucent
        effect.blendingMode = .behindWindow
        effect.state = .active
        effect.appearance = NSAppearance(named: .darkAqua)
        effect.frame = bounds
        effect.autoresizingMask = [.width, .height]
        addSubview(effect)

        // Solid graphite tint over the beak only — exactly the color the PanelView body
        // gradient carries at its top edge (Color(0.125,0.122,0.118).opacity(0.30)), where
        // the beak joins. A *flat* fill (both stops equal) is deliberate: the beak is only
        // ~26pt tall, so the body gradient barely shifts across it, and a solid fill is
        // immune to CAGradientLayer's y-orientation (which is bottom-up on a non-flipped
        // macOS layer). The whole beak therefore reads as one continuous surface with the
        // header — no seam at the join, no mis-tinted tip. Rendered above the vibrancy.
        let beakTint = NSColor(red: 0.125, green: 0.122, blue: 0.118, alpha: 0.30).cgColor
        beakGradient.colors = [beakTint, beakTint]
        layer?.addSublayer(beakGradient)

        applyMask()
        updateBeakGradient()
    }
    required init?(coder: NSCoder) { fatalError("unused") }

    private func bodyPath() -> NSBezierPath {
        NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: bounds.width, height: PANEL_H),
                     xRadius: CORNER, yRadius: CORNER)
    }

    /// A smooth "beak", not a triangle: a raised-cosine bump (`h·½(1+cos πt)`) whose
    /// flanks leave the flat top edge with a horizontal tangent, dip through concave
    /// shoulders, and curve over a softly rounded apex — so the arrow flows *out* of
    /// the body instead of rising from a kink. Sampled as a fine polyline; it's
    /// rasterised into the mask anyway, so a curve beats fiddly Bézier control points.
    /// Filled separately from the body (see applyMask) so the two never cancel.
    private func beakPath() -> NSBezierPath {
        let cx = max(ARROW_CLAMP, min(arrowX, bounds.width - ARROW_CLAMP))
        let w = ARROW_W / 2, h = ARROW_H, y0 = PANEL_H - 2   // base sits just inside the body
        let beak = NSBezierPath()
        let steps = 120
        beak.move(to: NSPoint(x: cx - w, y: y0))
        for i in 0...steps {
            let t = CGFloat(i) / CGFloat(steps) * 2 - 1       // -1 … 1
            beak.line(to: NSPoint(x: cx + t * w, y: y0 + h * 0.5 * (1 + cos(.pi * t))))
        }
        beak.line(to: NSPoint(x: cx + w, y: y0))
        beak.close()
        return beak
    }

    override func viewDidChangeBackingProperties() {
        super.viewDidChangeBackingProperties()
        applyMask()
        updateBeakGradient()
    }

    override func layout() {
        super.layout()
        updateBeakGradient()
    }

    // Rasterize the bubble+arrow at the display's backing scale so the mask edge
    // stays crisp on Retina.
    private func applyMask() {
        guard bounds.width > 0, bounds.height > 0 else { return }
        let scale = window?.backingScaleFactor ?? 2
        let pw = Int((bounds.width * scale).rounded()), ph = Int((bounds.height * scale).rounded())
        guard let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: pw, pixelsHigh: ph,
                bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0) else { return }
        rep.size = bounds.size
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
        NSColor.black.setFill()
        // Two separate fills = union by overpaint. Appending the beak to the body as
        // one path made their overlap cancel under nonzero winding, leaving a white
        // slit at the join — the "not smooth" seam between box and arrow.
        bodyPath().fill()
        beakPath().fill()
        NSGraphicsContext.restoreGraphicsState()
        let img = NSImage(size: bounds.size)
        img.addRepresentation(rep)
        effect.maskImage = img
    }

    // Position the beak gradient CALayer over the beak region with a matching clip mask,
    // so only the beak area gets the graphite tint — not the body (SwiftUI covers that).
    private func updateBeakGradient() {
        guard bounds.width > 0 else { return }
        let cx = max(ARROW_CLAMP, min(arrowX, bounds.width - ARROW_CLAMP))
        let w = ARROW_W / 2
        // Beak region: a tight rect enclosing just the arrow, with a small margin.
        let margin: CGFloat = 4
        let beakRect = CGRect(x: cx - w - margin, y: PANEL_H - 2,
                              width: (w + margin) * 2, height: ARROW_H + 2)
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        beakGradient.frame = beakRect
        // Clip the gradient to the exact beak shape using the rasterised bitmap mask.
        let scale = window?.backingScaleFactor ?? 2
        let pw = Int((beakRect.width * scale).rounded())
        let ph = Int((beakRect.height * scale).rounded())
        guard pw > 0, ph > 0,
              let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: pw, pixelsHigh: ph,
                      bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                      colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0) else {
            CATransaction.commit(); return
        }
        rep.size = beakRect.size
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
        // Translate the path into beak-local coordinates.
        let xform = AffineTransform(translationByX: -(cx - w - margin), byY: -(PANEL_H - 2))
        let localPath = beakPath()
        localPath.transform(using: xform)
        NSColor.black.setFill()
        localPath.fill()
        NSGraphicsContext.restoreGraphicsState()
        let maskImg = NSImage(size: beakRect.size)
        maskImg.addRepresentation(rep)
        let maskLayer = CALayer()
        maskLayer.frame = CGRect(origin: .zero, size: beakRect.size)
        maskLayer.contents = maskImg
        beakGradient.mask = maskLayer
        CATransaction.commit()
    }
}

@MainActor
final class AppController: NSObject, NSApplicationDelegate, UNUserNotificationCenterDelegate {
    let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    let model = KeeperModel(port: PORT)
    var panel: KeyablePanel!
    var glassSurface: GlassSurface?
    var server: Process?
    var repoMissing = false
    var clickMonitor: Any?
    var escMonitor: Any?
    var notifDrainTimer: Timer?

    func applicationDidFinishLaunching(_ note: Notification) {
        // Dev-only: KEEPER_PREVIEW renders the panel in a normal window for a
        // screenshot of the live glass material (the menu-bar popover is hidden
        // until clicked and can't be captured headlessly).
        if ProcessInfo.processInfo.environment["KEEPER_PREVIEW"] != nil {
            startServer()
            NSApp.setActivationPolicy(.regular)
            // Borderless, like the real panel, so the screenshot shows the true chrome
            // (arrow, rounded corners, shadow) — not a titlebar window.
            let total = NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H + ARROW_H)
            panel = KeyablePanel(contentRect: total, styleMask: [.borderless, .nonactivatingPanel],
                                 backing: .buffered, defer: false)
            panel.isFloatingPanel = true
            panel.level = .popUpMenu
            panel.isOpaque = false
            panel.backgroundColor = .clear
            panel.hasShadow = true
            panel.contentView = makeGlassContent()
            setArrowX(PANEL_W - 40)
            if let vf = NSScreen.main?.visibleFrame {
                panel.setFrameTopLeftPoint(NSPoint(x: vf.minX + 140, y: vf.maxY - 40))
            }
            if let t = ProcessInfo.processInfo.environment["KEEPER_TAB"], let tab = Tab(rawValue: t) {
                model.tab = tab
            }
            panel.makeKeyAndOrderFront(nil)
            panel.invalidateShadow()
            NSApp.activate(ignoringOtherApps: true)
            model.onPanelOpen()
            return
        }
        // Menu-bar path: put the icon on screen FIRST, before any disk work. On a
        // fresh install startServer() copies the whole bundled payload into
        // Application Support (seedFromBundle) — synchronous file IO that must never
        // delay or hide the status item. So we set up the UI, then boot the server
        // off the main thread. The model already polls the server with retries on
        // panel open, so the icon never waits on the server coming up.
        NSApp.setActivationPolicy(.accessory)
        setupStatusItem()
        setupPanel()
        setupNotifications()
        startServerAsync()

        // First-run safety net: a brand-new user's only UI is the menu-bar icon. If
        // the bar is full or the icon lands under the notch, the system gives the item
        // no window and nothing shows — the app looks dead though it's running. Pop the
        // onboarding panel (centred via positionPanel's fallback) so first launch is
        // always visible and setup is reachable regardless of the icon.
        if !hasConnectedAccount() { showPanel() }
    }

    // Re-opening the app from Finder/Spotlight (the natural move when you can't find
    // the menu-bar icon) re-shows the panel instead of silently doing nothing.
    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        showPanel()
        return true
    }

    // MARK: notifications

    /// Own notifications at the app level so they carry the app icon and a tap
    /// opens the panel on Open loops. Runs drop a one-shot via the server; we drain
    /// it on launch, on a light timer (catches scheduled runs while idle), and the
    /// model also drains the instant a manual run finishes.
    private func setupNotifications() {
        UNUserNotificationCenter.current().delegate = self
        RunNotifier.requestAuthorization()
        Task { await model.drainPendingNotification() }
        notifDrainTimer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            guard let self else { return }
            Task { @MainActor in await self.model.drainPendingNotification() }
        }
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter,
                                            willPresent notification: UNNotification,
                                            withCompletionHandler completionHandler:
                                                @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])   // show even though we're a menu-bar app
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter,
                                            didReceive response: UNNotificationResponse,
                                            withCompletionHandler completionHandler: @escaping () -> Void) {
        Task { @MainActor in
            self.model.tab = .loops
            self.showPanel()
            completionHandler()
        }
    }

    /// Build the dark frosted surface (masked vibrancy, body + arrow) hosting the
    /// SwiftUI panel. The vibrancy is the surface; the SwiftUI content sits on top
    /// clipped to the rounded body.
    func makeGlassContent() -> NSView {
        let dark = NSAppearance(named: .darkAqua)
        let total = NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H + ARROW_H)
        let bodyRect = NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H)

        let surface = GlassSurface(frame: total)
        glassSurface = surface

        let hosting = NSHostingView(rootView: PanelView().environmentObject(model))
        hosting.frame = bodyRect
        hosting.wantsLayer = true
        hosting.layer?.backgroundColor = .clear
        hosting.layer?.cornerRadius = CORNER
        hosting.layer?.cornerCurve = .continuous
        hosting.layer?.masksToBounds = true
        hosting.appearance = dark
        surface.addSubview(hosting)                   // content on top of the vibrancy
        return surface
    }

    func setArrowX(_ x: CGFloat) { glassSurface?.arrowX = x }

    func setupStatusItem() {
        if let button = statusItem.button {
            if let img = NSImage(systemSymbolName: "tray.full", accessibilityDescription: "zero") {
                img.isTemplate = true
                button.image = img
            } else {
                // Fallback so the item is never zero-width (= invisible) if the SF
                // Symbol can't be loaded — a menu-bar app with no image and no title
                // renders nothing at all.
                button.title = "zero"
            }
            button.action = #selector(statusItemClicked)
            button.target = self
            // Receive both mouse-up events so we can distinguish right-click.
            button.sendAction(on: [.leftMouseUp, .rightMouseUp])
        }
    }

    @objc func statusItemClicked() {
        guard NSApp.currentEvent?.type == .rightMouseUp else { togglePanel(); return }
        // Right-click: show a single "Quit zero" NSMenu, then clear it so
        // the next left-click still goes through togglePanel (not the menu).
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String
        let menu = NSMenu()
        if let v = version {
            let versionItem = NSMenuItem(title: "zero \(v)", action: nil, keyEquivalent: "")
            versionItem.isEnabled = false
            menu.addItem(versionItem)
            menu.addItem(.separator())
        }
        menu.addItem(NSMenuItem(title: "Quit zero", action: #selector(NSApplication.terminate(_:)),
                                keyEquivalent: "q"))
        statusItem.menu = menu
        statusItem.button?.performClick(nil)   // open the menu
        statusItem.menu = nil                  // clear immediately so left-click stays toggle
    }

    func setupPanel() {
        let content = NSRect(x: 0, y: 0, width: PANEL_W, height: PANEL_H + ARROW_H)
        let glass = makeGlassContent()

        panel = KeyablePanel(contentRect: content,
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
        panel.contentView = glass
    }

    @objc func togglePanel() {
        if panel.isVisible { hidePanel() } else { showPanel() }
    }

    func showPanel() {
        removeMonitors()                    // never double-register (showPanel without a paired hide)
        positionPanel()
        model.onPanelOpen()                 // reload + re-attach to any live job (never reload-blow-away)
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
        removeMonitors()
    }

    func removeMonitors() {
        if let m = clickMonitor { NSEvent.removeMonitor(m); clickMonitor = nil }
        if let m = escMonitor { NSEvent.removeMonitor(m); escMonitor = nil }
    }

    // Snug under the menu-bar item: the arrow tip sits just below the bar, pointing
    // at the item's centre; the window is clamped to the screen.
    func positionPanel() {
        // If the status item has no on-screen window, the system couldn't place the
        // icon — the menu bar is full or it's hidden under the notch (the classic
        // "menu-bar app runs but shows no icon" case). Don't bail and leave the panel
        // off-screen: centre it near the top of the main screen so it's always visible
        // and the user can still see + use zero (and finish onboarding).
        guard let button = statusItem.button, let bWin = button.window else {
            centerPanelOnScreen()
            return
        }
        let f = bWin.convertToScreen(button.convert(button.bounds, to: nil))
        let visible = (bWin.screen ?? NSScreen.main)?.visibleFrame
            ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let winH = PANEL_H + ARROW_H
        var originX = f.midX - (PANEL_W - 40)
        originX = max(visible.minX + 8, min(originX, visible.maxX - PANEL_W - 8))
        let originY = f.minY - GAP - winH
        setArrowX(f.midX - originX)                  // item centre in window coords
        panel.setFrame(NSRect(x: originX, y: originY, width: PANEL_W, height: winH), display: true)
        panel.invalidateShadow()                     // shadow follows the rounded glass silhouette
    }

    // Fallback placement when there's no menu-bar item to anchor to (full bar / notch):
    // top-centre of the main screen, arrow pointed at its own centre, fully on-screen.
    func centerPanelOnScreen() {
        let winH = PANEL_H + ARROW_H
        let visible = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let originX = visible.midX - PANEL_W / 2
        let originY = visible.maxY - winH - 12
        setArrowX(PANEL_W / 2)
        panel.setFrame(NSRect(x: originX, y: originY, width: PANEL_W, height: winH), display: true)
        panel.invalidateShadow()
    }

    /// Build and launch the Python keeper server. Pure (no main-actor state) so it
    /// can run off the main thread on first launch, where resolveRepoRoot()/
    /// seedFromBundle() do synchronous payload-copy disk IO. Returns nil on failure.
    nonisolated static func launchServer(root: String) -> Process? {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        p.arguments = ["python3", "\(root)/lib/keeper_server.py"]
        var env = ProcessInfo.processInfo.environment
        env["PATH"] = augmentedPath()
        env["GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND"] = "file"
        env["KEEPER_PORT"] = PORT
        env["MAIL_TRIAGE_DIR"] = root
        // gws uses per-account keyring creds, never a global token. Strip any stray
        // GOOGLE_WORKSPACE_CLI_TOKEN (e.g. exported from the user's shell) so it can't
        // poison the Authorization header and break every account.
        env.removeValue(forKey: "GOOGLE_WORKSPACE_CLI_TOKEN")
        p.environment = env
        p.currentDirectoryURL = URL(fileURLWithPath: root)
        do { try p.run(); return p } catch { return nil }
    }

    // Synchronous boot — used by the dev/preview path that needs the server up
    // before it renders the screenshot window.
    func startServer() {
        guard let root = resolveRepoRoot(), let p = Self.launchServer(root: root) else {
            repoMissing = true
            return
        }
        server = p
    }

    // Menu-bar boot — resolve the root (copies the bundled payload on first launch)
    // and launch the server entirely off the main thread, so the status item that
    // was already put up in applicationDidFinishLaunching is never blocked by disk IO.
    func startServerAsync() {
        // Strong self: AppController is the app delegate and lives for the whole
        // process, so there's nothing to leak and nothing to outlive.
        Task.detached(priority: .userInitiated) {
            let proc = resolveRepoRoot().flatMap { Self.launchServer(root: $0) }
            await MainActor.run {
                if let proc { self.server = proc } else { self.repoMissing = true }
            }
        }
    }

    func applicationWillTerminate(_ note: Notification) {
        server?.terminate()
    }
}

// Top-level entry runs on the main thread; assert that to the concurrency checker.
MainActor.assumeIsolated {
    let app = NSApplication.shared
    let controller = AppController()
    app.delegate = controller
    app.run()
}
