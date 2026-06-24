// Style.swift — the brand's warm-paper palette (ported from the panel's OKLCH
// tokens to sRGB) and a few reusable SwiftUI pieces. Light theme only; the surface
// underneath is real Liquid Glass (NSGlassEffectView), so content here is opaque
// ink on translucent warm surfaces — never glass-on-glass.

import SwiftUI

extension Color {
    init(_ r: Double, _ g: Double, _ b: Double, _ a: Double = 1) {
        self.init(.sRGB, red: r, green: g, blue: b, opacity: a)
    }
    /// Parse "#RRGGBB" (the per-account color the server hands us).
    init(hex: String) {
        let s = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
        var v: UInt64 = 0; Scanner(string: s).scanHexInt64(&v)
        self.init(Double((v >> 16) & 0xff) / 255, Double((v >> 8) & 0xff) / 255, Double(v & 0xff) / 255)
    }
}

// Dark "Raycast" theme. The surface is dark translucent glass; text is bright warm
// off-white; terracotta stays the single accent. `raised` is a near-white meant to
// be used at LOW alpha as a lifting overlay; `sunken` is near-black for recessed
// insets; `paper` is a solid charcoal for opaque surfaces (composer, toast).
enum Paper {
    static let paper       = Color(0.135, 0.128, 0.122)   // solid dark surface
    static let raised      = Color(0.97, 0.96, 0.94)      // light overlay (use at low alpha)
    static let sunken      = Color(0.0, 0.0, 0.0)         // dark inset (use at low alpha)
    static let ink         = Color(0.95, 0.94, 0.92)      // primary text
    static let ink2        = Color(0.78, 0.76, 0.73)
    static let ink3        = Color(0.60, 0.585, 0.55)
    static let ink4        = Color(0.47, 0.455, 0.43)
    static let hairline    = Color(1.0, 1.0, 1.0)         // dividers (use at low alpha)
    static let accent      = Color(0.87, 0.52, 0.40)      // terracotta, brightened for dark
    static let accentPress = Color(0.79, 0.45, 0.34)
    static let accentSoft  = Color(0.90, 0.62, 0.50)      // accent text on dark (toast undo)
    static let clear       = Color(0.46, 0.78, 0.58)      // reward green
    static let danger      = Color(0.91, 0.46, 0.43)
}

// Compact relative time: "now", "5m", "3h", "2d", "1w", "2mo".
func relTime(_ epoch: Int) -> String {
    guard epoch > 0 else { return "" }
    let s = max(0, Int(Date().timeIntervalSince1970) - epoch)
    if s < 90 { return "now" }
    let m = s / 60; if m < 60 { return "\(m)m" }
    let h = m / 60; if h < 24 { return "\(h)h" }
    let d = h / 24; if d < 7 { return "\(d)d" }
    let w = d / 7; if w < 5 { return "\(w)w" }
    return "\(d / 30)mo"
}

// The single tinted call-to-action. Solid terracotta (not glass) so it reads as
// the one primary action over the glass surface, per Apple's "tint = one thing".
struct PrimaryButtonStyle: ButtonStyle {
    var enabled: Bool = true
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .semibold))
            .foregroundStyle(.white)
            .padding(.horizontal, 15).frame(height: 34)
            .background(
                RoundedRectangle(cornerRadius: 9, style: .continuous)
                    .fill(configuration.isPressed ? Paper.accentPress : Paper.accent)
            )
            .opacity(enabled ? 1 : 0.55)
            .contentShape(Rectangle())
    }
}

// Quiet secondary action: hairline-bordered warm chip.
struct GhostButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 12.5, weight: .medium))
            .foregroundStyle(Paper.ink2)
            .padding(.horizontal, 13).frame(height: 30)
            .background(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(Paper.raised.opacity(configuration.isPressed ? 0.16 : 0.08))
                    .overlay(RoundedRectangle(cornerRadius: 8, style: .continuous)
                        .strokeBorder(Paper.hairline.opacity(0.14), lineWidth: 0.5))
            )
            .contentShape(Rectangle())
    }
}

// Small initials chip (account color), used in rows + cards + the top strip.
struct InitialsChip: View {
    let text: String
    let color: Color
    var size: CGFloat = 26
    var body: some View {
        Text(text)
            .font(.system(size: size * 0.38, weight: .bold))
            .foregroundStyle(.white)
            .frame(width: size, height: size)
            .background(RoundedRectangle(cornerRadius: size * 0.27, style: .continuous).fill(color))
    }
}
