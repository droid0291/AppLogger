import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Hang")

struct HangDemoView: View {
    @State private var statusText = "Tap a button to simulate a main-thread hang."
    @State private var isHanging = false

    var body: some View {
        DemoPage(title: "Hang Demo (ANR equiv)", items: [
            DemoItem(
                label: "Block Main Thread 5s",
                description: "Thread.sleep() on main thread — UI freezes (spinner appears)",
                color: "#FFB347"
            ) { hang(seconds: 5) },

            DemoItem(
                label: "Block Main Thread 15s",
                description: "Sustained freeze — Xcode/instruments reports main-thread watchdog hit",
                color: "#FF6B6B"
            ) { hang(seconds: 15) },

            DemoItem(
                label: "Busy Loop on Main Thread",
                description: "CPU-intensive work on UI thread — jank + frame drops",
                color: "#FFB347"
            ) { busyLoop() },
        ], footerNote: statusText)
    }

    private func hang(seconds: Int) {
        log.error(">>> Hang: blocking main thread for \(seconds)s")
        statusText = "⏳ Hanging for \(seconds)s…"
        isHanging = true
        Thread.sleep(forTimeInterval: TimeInterval(seconds))  // ← intentional main-thread block
        statusText = "✅ Survived \(seconds)s hang"
        log.warning("Hang ended after \(seconds)s — UI was frozen")
        isHanging = false
    }

    private func busyLoop() {
        log.error(">>> Hang: starting 5-second CPU busy loop on main thread")
        statusText = "🔥 Busy-looping for 5s…"
        let end = Date().addingTimeInterval(5)
        while Date() < end {
            _ = sqrt(Double.random(in: 0...1))
        }
        statusText = "✅ Busy loop completed"
        log.warning("Main-thread busy loop ended")
    }
}
