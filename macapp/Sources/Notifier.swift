// Native run-complete notifications, owned by the app bundle.
//
// Because the app posts these (not osascript), they carry the app icon, and
// AppController's UNUserNotificationCenterDelegate opens the panel on Open loops
// when one is tapped. The notification body is authored server-side; the app
// only relays it.

import Foundation
import UserNotifications

enum RunNotifier {
    /// Ask once for permission to show banners. No-op if already decided.
    static func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    static func post(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title.isEmpty ? "zero" : title
        content.body = body
        content.sound = .default
        content.userInfo = ["target": "loops"]   // tap → Open loops
        let req = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(req)
    }

    /// A new version is ready. Stable id keyed by version so re-checks don't stack
    /// duplicates. Tap → open the changelog.
    static func postUpdateAvailable(version: String, url: String) {
        postUpdate(id: "zero-update-\(version)", title: "Update available",
                   body: "zero \(version) is ready to install. Open zero to update — tap to see what's new.",
                   url: url)
    }

    /// The update has applied and we've relaunched on the new build. Tap → changelog.
    static func postUpdated(version: String, url: String) {
        postUpdate(id: "zero-updated-\(version)", title: "zero updated",
                   body: "You're now on \(version). Tap to see what's new.", url: url)
    }

    private static func postUpdate(id: String, title: String, body: String, url: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.userInfo = ["target": "url", "url": url]   // tap → open the changelog
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: id, content: content, trigger: nil))
    }
}
