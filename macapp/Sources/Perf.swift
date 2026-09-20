import Foundation
import QuartzCore

// Opt-in performance diagnostics. Off unless ZERO_PERF=1; when off, `tick` is a
// single boolean test and the hitch monitor is never started, so shipping builds
// pay nothing.
//
// WHY THIS EXISTS: "the app feels laggy" was diagnosed several times by reading
// code and guessing. Each guess found *a* real cost without fixing the felt
// problem, because counting work does not tell you which work BLOCKED. Synthetic
// CGEvent scrolls do not reach a non-activating status-item panel either, so the
// only honest signal is measuring the real main thread while a human drives it.
//
// Usage:
//     ZERO_PERF=1 /Applications/zero.app/Contents/MacOS/zero
// then use the app. Two kinds of line appear on stderr:
//
//     HITCH  312 ms   main thread blocked      <- a dropped-frame stall, with duration
//     PERF/s rowBody=1841  listBody=97         <- how much work happened in that second
//
// A HITCH is the thing the user actually feels. The counters next to it say why.
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
        write("PERF/s  " + body)
    }

    /// Time a named block and report it if it blocks longer than `warn`.
    /// Use around anything suspected of running on the main thread at the wrong time.
    @discardableResult
    static func measure<T>(_ what: String, warn: Double = 0.016,
                           _ body: () throws -> T) rethrows -> T {
        guard on else { return try body() }
        let t0 = CACurrentMediaTime()
        let out = try body()
        let dt = CACurrentMediaTime() - t0
        if dt > warn {
            write(String(format: "SLOW   %6.1f ms   %@", dt * 1000, what))
        }
        return out
    }

    /// Watch the main run loop and report every stall longer than one frame.
    ///
    /// This is the measurement that matters: it does not care WHY the main thread
    /// was busy, only that it was unavailable, which is exactly what "laggy" means.
    /// A timer that should fire every 8 ms but fires 300 ms late proves a 300 ms
    /// block, whatever caused it.
    static func startHitchMonitor() {
        guard on else { return }
        var last = CACurrentMediaTime()
        let interval = 0.008
        let timer = Timer(timeInterval: interval, repeats: true) { _ in
            let now = CACurrentMediaTime()
            let gap = now - last
            last = now
            // One dropped frame at 60 Hz is ~16.7 ms; 33 ms means at least two.
            if gap > 0.033 {
                write(String(format: "HITCH  %6.1f ms   main thread blocked", gap * 1000))
            }
        }
        // .common so the stall is still observed during scroll tracking, which is
        // precisely when the default run loop mode would stop firing it.
        RunLoop.main.add(timer, forMode: .common)
        write("perf: hitch monitor on (reporting stalls > 33 ms)")
    }

    private static func write(_ line: String) {
        FileHandle.standardError.write(Data((line + "\n").utf8))
    }
}
