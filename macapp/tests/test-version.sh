#!/bin/bash
# Runnable check for versionIsNewer / releaseVersion (Sources/Version.swift).
# Compiles the REAL source with a throwaway test main, so there's zero logic
# duplication. Fails loudly if the version compare ever breaks.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"          # macapp/
TMP="$(mktemp -d)"; MAIN="$TMP/main.swift"
cat > "$MAIN" <<'SWIFT'
import Foundation
func check(_ c: Bool, _ m: String) {
    if !c { FileHandle.standardError.write(Data("FAIL: \(m)\n".utf8)); exit(1) }
}
check(versionIsNewer("1.6.19", than: "1.6.18"),  "patch bump")
check(versionIsNewer("1.7.0",  than: "1.6.18"),  "minor bump")
check(versionIsNewer("2.0.0",  than: "1.9.9"),   "major bump")
check(versionIsNewer("1.6.18.1", than: "1.6.18"),"extra component newer")
check(!versionIsNewer("1.6.18", than: "1.6.18"), "equal is not newer")
check(!versionIsNewer("1.6.17", than: "1.6.18"), "older is not newer")
check(!versionIsNewer("1.6",    than: "1.6.0"),  "1.6 == 1.6.0")
check(releaseVersion(fromTag: "v1.6.19") == "1.6.19", "strip leading v")
check(releaseVersion(fromTag: "1.6.19")  == "1.6.19", "no-v passthrough")
print("version_test OK")
SWIFT
swiftc "$DIR/Sources/Version.swift" "$MAIN" -o "$TMP/vt"
"$TMP/vt"
