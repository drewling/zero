import Foundation

// Opt-in scroll diagnostics. Off unless ZERO_PERF=1, and compiled to nothing more
// than an `if` when off, so shipping builds pay nothing.
//
// WHY THIS EXISTS: "scrolling is laggy" was diagnosed three times by reading the
// code and guessing, and each guess found *a* real cost without fixing the felt
// problem. Synthetic CGEvent scrolls do not reach this panel (it is a non-activating
// status-item window), so the only honest way to measure is to count the work the
// app actually does while a human scrolls it.
//
// Usage:  ZERO_PERF=1 /Applications/zero.app/Contents/MacOS/zero
// then scroll the list and read the summary lines on stderr.
enum Perf {
    static let on = ProcessInfo.processInfo.environment["ZERO_PERF"] == "1"

    private static var counts: [String: Int] = [:]
    private static var lastReport = Date()
    private static let lock = NSLock()

    /// Count one occurrence of `what`. Cheap: a dictionary bump behind a lock.
    static func tick(_ what: String) {
        guard on else { return }
        lock.lock()
        counts[what, default: 0] += 1
        let now = Date()
        let due = now.timeIntervalSince(lastReport) >= 1.0
        var snapshot: [String: Int] = [:]
        if due {
            snapshot = counts
            counts.removeAll()
            lastReport = now
        }
        lock.unlock()
        guard due, !snapshot.isEmpty else { return }
        let body = snapshot.sorted { $0.value > $1.value }
            .map { "\($0.key)=\($0.value)" }.joined(separator: "  ")
        FileHandle.standardError.write(Data(("PERF/s  " + body + "\n").utf8))
    }
}
