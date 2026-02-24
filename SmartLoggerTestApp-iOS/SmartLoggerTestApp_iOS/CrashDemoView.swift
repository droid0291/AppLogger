import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Crash")

struct CrashDemoView: View {
    var body: some View {
        DemoPage(title: "Crash Demo", items: [
            DemoItem(
                label: "Force-Unwrap Nil (NPE)",
                description: "Unwraps an Optional that is nil → Fatal error",
                color: "#FF6B6B"
            ) { triggerNilCrash() },

            DemoItem(
                label: "Out of Memory",
                description: "Allocates arrays until memory pressure kills the app",
                color: "#FF6B6B"
            ) { triggerOOM() },

            DemoItem(
                label: "Stack Overflow",
                description: "Infinite recursion exceeds the call stack limit",
                color: "#FF6B6B"
            ) { triggerStackOverflow() },

            DemoItem(
                label: "Index Out of Bounds",
                description: "Accesses index 99 on a 3-element array",
                color: "#FF6B6B"
            ) { triggerIndexOutOfBounds() },
        ])
    }
}

// MARK: - Crash helpers

private func triggerNilCrash() {
    log.error(">>> Triggering force-unwrap nil — Fatal error incoming")
    let result: [String]? = loadTransactions()
    _ = result!.count   // crashes here
}

private func loadTransactions() -> [String]? { nil }

private func triggerOOM() {
    log.error(">>> Triggering OOM — allocating arrays until memory pressure kills app")
    var sink: [[UInt8]] = []
    while true {
        sink.append([UInt8](repeating: 0, count: 10_000_000)) // 10 MB
    }
}

private func triggerStackOverflow() {
    log.error(">>> Triggering stack overflow via infinite recursion")
    triggerStackOverflow()          // no base case
}

private func triggerIndexOutOfBounds() {
    log.error(">>> Triggering index out of bounds — accessing index 99 on 3-element array")
    let items = ["apple", "banana", "cherry"]
    let bad = items[99]             // crashes here
    log.debug("Value: \(bad)")      // never reached
}
