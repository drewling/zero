// Version.swift — pure version helpers for the self-updater. Foundation only (no
// AppKit/SwiftUI) so it compiles standalone for the runnable check in
// macapp/tests/test-version.sh. The networking + install live in Updater.swift.

import Foundation

// GitHub "latest release" payload — only the fields the updater reads.
struct GithubRelease: Decodable {
    let tagName: String
    let htmlURL: String
    let body: String?
    enum CodingKeys: String, CodingKey {
        case tagName = "tag_name"
        case htmlURL = "html_url"
        case body
    }
    /// Release version without the leading "v" (tags are "v1.6.19").
    var version: String { releaseVersion(fromTag: tagName) }
}

/// Strip a leading "v" from a release tag ("v1.6.19" → "1.6.19").
func releaseVersion(fromTag tag: String) -> String {
    tag.hasPrefix("v") ? String(tag.dropFirst()) : tag
}

/// True iff `candidate` is strictly newer than `current`, comparing dotted numeric
/// components ("1.6.18"). Missing/non-numeric components count as 0.
// ponytail: integer-dotted only — tags are clean vX.Y.Z. Add pre-release/build
// suffix ordering only if tags ever start carrying them.
func versionIsNewer(_ candidate: String, than current: String) -> Bool {
    func parts(_ s: String) -> [Int] {
        s.split(separator: ".").map { Int($0.prefix(while: \.isNumber)) ?? 0 }
    }
    let a = parts(candidate), b = parts(current)
    for i in 0..<max(a.count, b.count) {
        let x = i < a.count ? a[i] : 0
        let y = i < b.count ? b[i] : 0
        if x != y { return x > y }
    }
    return false
}
