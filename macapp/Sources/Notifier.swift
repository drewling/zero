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
}
