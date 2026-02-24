import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Performance")

// Global static sink — intentionally not cleaned up (simulates a retain cycle / memory leak)
private var leakedObjects: [AnyObject] = []

struct PerformanceDemoView: View {
    @State private var leakStatus = "Leaked objects: 0"
    @State private var cpuStatus  = "Idle"
    @State private var cpuRunning = false
    @State private var cpuTask: Task<Void, Never>? = nil

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {

                // 1. Memory Leak
                SectionCard(title: "1. Memory Leak") {
                    StatusLabel(text: leakStatus)
                    HStack(spacing: 12) {
                        ActionButton(label: "Leak 500 Objects") { leakMemory() }
                        ActionButton(label: "Clear", color: "#444466") { clearLeak() }
                    }
                }

                // 2. CPU Spike
                SectionCard(title: "2. CPU Spike (15s)") {
                    StatusLabel(text: cpuStatus)
                    ActionButton(label: cpuRunning ? "⏹ Stop CPU Spike" : "▶ Start CPU Spike",
                                 color: cpuRunning ? "#444466" : "#FF6B6B") {
                        if cpuRunning { stopCpu() } else { startCpu() }
                    }
                }
            }
            .padding(16)
        }
        .background(Color(hex: "#0D0D1A"))
        .navigationTitle("Performance Demo")
        .navigationBarTitleDisplayMode(.inline)
        .onDisappear { cpuTask?.cancel() }
    }

    // MARK: - Memory Leak

    private func leakMemory() {
        log.warning(">>> Memory Leak: Adding 500 objects to static array (retained indefinitely)")
        for i in 0..<500 {
            leakedObjects.append(NSObject() as AnyObject)
            _ = i
        }
        leakStatus = "Leaked objects: \(leakedObjects.count)"
    }

    private func clearLeak() {
        leakedObjects.removeAll()
        leakStatus = "Leaked objects: 0 (cleared)"
        log.info("Memory Leak: Static array cleared — GC can now reclaim")
    }

    // MARK: - CPU Spike

    private func startCpu() {
        log.warning(">>> Performance: Starting CPU busy loop for 15 seconds")
        cpuRunning = true
        cpuStatus = "🔥 Running…"

        cpuTask = Task.detached(priority: .userInitiated) {
            let end = Date().addingTimeInterval(15)
            var iterations = 0
            while !Task.isCancelled && Date() < end {
                _ = sqrt(Double.random(in: 0...1))
                iterations += 1
                if iterations % 1_000_000 == 0 {
                    let remaining = Int(end.timeIntervalSinceNow)
                    log.warning("CPU spike running… \(remaining)s remaining")
                    await MainActor.run {
                        cpuStatus = "🔥 Running… \(remaining)s remaining"
                    }
                }
            }
            log.info("CPU spike ended after \(iterations) iterations")
            await MainActor.run {
                cpuStatus = "Idle (completed)"
                cpuRunning = false
            }
        }
    }

    private func stopCpu() {
        cpuTask?.cancel()
        cpuRunning = false
        cpuStatus = "Stopped by user"
        log.info("CPU Spike stopped by user")
    }
}
