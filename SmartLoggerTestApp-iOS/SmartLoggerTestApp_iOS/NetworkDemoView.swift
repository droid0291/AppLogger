import SwiftUI
import OSLog
import Network

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Network")

struct NetworkDemoView: View {
    @State private var timeoutStatus  = "Tap to connect to a non-routable host."
    @State private var http500Status  = "Tap to request HTTP 500."
    @State private var offlineStatus  = "Tap to check connectivity then attempt API call."
    @State private var timeoutBusy  = false
    @State private var http500Busy  = false
    @State private var offlineBusy  = false

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {

                // 1. Timeout
                SectionCard(title: "1. Network Timeout") {
                    StatusLabel(text: timeoutStatus)
                    ActionButton(label: "Trigger Timeout", disabled: timeoutBusy) {
                        triggerTimeout()
                    }
                }

                // 2. HTTP 500
                SectionCard(title: "2. HTTP 500 — Server Error") {
                    StatusLabel(text: http500Status)
                    ActionButton(label: "Trigger HTTP 500", disabled: http500Busy) {
                        triggerHttp500()
                    }
                }

                // 3. Offline
                SectionCard(title: "3. Offline — No Connectivity") {
                    StatusLabel(text: offlineStatus)
                    ActionButton(label: "Check & Make Request", disabled: offlineBusy) {
                        triggerOffline()
                    }
                }
            }
            .padding(16)
        }
        .background(Color(hex: "#0D0D1A"))
        .navigationTitle("Network Demo")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Timeout

    private func triggerTimeout() {
        timeoutBusy = true
        timeoutStatus = "⏳ Connecting to non-routable host (10.255.255.1)…"
        log.error(">>> Network: Simulating connection timeout to 10.255.255.1")

        Task.detached {
            var request = URLRequest(url: URL(string: "http://10.255.255.1/api/data")!)
            request.timeoutInterval = 8
            do {
                _ = try await URLSession.shared.data(for: request)
                await MainActor.run {
                    timeoutStatus = "✅ Connected (unexpected)"
                    timeoutBusy = false
                }
            } catch let error as URLError where error.code == .timedOut {
                log.error("Network Timeout: \(error.localizedDescription)")
                await MainActor.run {
                    timeoutStatus = "❌ URLError.timedOut: \(error.localizedDescription)\n\nBug: App shows blank screen instead of an error state."
                    timeoutBusy = false
                }
            } catch {
                log.error("Timeout sim error: \(error)")
                await MainActor.run {
                    timeoutStatus = "❌ \(error.localizedDescription)"
                    timeoutBusy = false
                }
            }
        }
    }

    // MARK: - HTTP 500

    private func triggerHttp500() {
        http500Busy = true
        http500Status = "⏳ Calling https://httpstat.us/500…"
        log.error(">>> Network: Requesting HTTP 500 from httpstat.us")

        Task.detached {
            do {
                let (_, response) = try await URLSession.shared.data(from: URL(string: "https://httpstat.us/500")!)
                let code = (response as? HTTPURLResponse)?.statusCode ?? -1
                log.error("HTTP Response: \(code)")
                await MainActor.run {
                    if code >= 500 {
                        http500Status = "❌ HTTP \(code) — Internal Server Error\n\nBug: App shows blank screen instead of a user-friendly error."
                    } else {
                        http500Status = "✅ HTTP \(code)"
                    }
                    http500Busy = false
                }
            } catch {
                log.error("HTTP 500 sim error: \(error)")
                await MainActor.run {
                    http500Status = "❌ \(error.localizedDescription)"
                    http500Busy = false
                }
            }
        }
    }

    // MARK: - Offline

    private func triggerOffline() {
        let monitor = NWPathMonitor()
        let queue = DispatchQueue(label: "NetworkMonitor")
        monitor.start(queue: queue)
        let path = monitor.currentPath
        monitor.cancel()

        let isConnected = path.status == .satisfied
        log.error(">>> Network: Offline check — connected=\(isConnected)")

        if isConnected {
            offlineStatus = "📶 You are ONLINE.\nTurn off Wi-Fi + Cellular, then tap again to see the error."
        } else {
            offlineStatus = "📵 No internet — making API call anyway (the bug)…"
            offlineBusy = true
            Task.detached {
                do {
                    _ = try await URLSession.shared.data(from: URL(string: "https://api.example.com/data")!)
                    await MainActor.run { offlineBusy = false }
                } catch {
                    log.error("Offline crash: \(error.localizedDescription)")
                    await MainActor.run {
                        offlineStatus = "❌ \(error.localizedDescription)\n\nBug: App crashed instead of showing offline banner."
                        offlineBusy = false
                    }
                }
            }
        }
    }
}
