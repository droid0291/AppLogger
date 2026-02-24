import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Main")

struct ContentView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                    NavigationLink { CrashDemoView() }    label: { DemoCard(icon: "💥", title: "Crash Demo",       desc: "NPE · OOM · Stack Overflow") }
                    NavigationLink { HangDemoView() }     label: { DemoCard(icon: "🥶", title: "Hang Demo",        desc: "Main-thread block (ANR equiv)") }
                    NavigationLink { UIBugDemoView() }    label: { DemoCard(icon: "🎨", title: "UI Bug Demo",      desc: "Overlap · Truncation · Contrast") }
                    NavigationLink { NetworkDemoView() }  label: { DemoCard(icon: "🌐", title: "Network Demo",     desc: "Timeout · HTTP 500 · Offline") }
                    NavigationLink { PerformanceDemoView() } label: { DemoCard(icon: "🔥", title: "Performance Demo", desc: "Memory Leak · CPU Spike") }
                    NavigationLink { SecurityDemoView() } label: { DemoCard(icon: "🔐", title: "Security Demo",    desc: "Hardcoded creds · Cleartext HTTP") }
                }
                .padding(16)
            }
            .background(Color(hex: "#0D0D1A"))
            .navigationTitle("SmartLogger Test")
            .navigationBarTitleDisplayMode(.large)
            .onAppear {
                log.info("SmartLoggerTestApp launched — ready to simulate bugs")
            }
        }
    }
}

// MARK: - Card

struct DemoCard: View {
    let icon: String
    let title: String
    let desc: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(icon).font(.system(size: 34))
            Text(title)
                .font(.system(size: 15, weight: .semibold))
                .foregroundColor(.white)
            Text(desc)
                .font(.system(size: 12))
                .foregroundColor(Color(hex: "#9090B0"))
                .fixedSize(horizontal: false, vertical: true)
            Spacer()
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 130, alignment: .topLeading)
        .background(Color(hex: "#1C1C2E"))
        .cornerRadius(14)
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color(hex: "#2E2E44"), lineWidth: 1))
    }
}

// MARK: - Color helper

extension Color {
    init(hex: String) {
        let h = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
        var rgb: UInt64 = 0
        Scanner(string: h).scanHexInt64(&rgb)
        self.init(
            red:   Double((rgb >> 16) & 0xFF) / 255,
            green: Double((rgb >>  8) & 0xFF) / 255,
            blue:  Double( rgb        & 0xFF) / 255
        )
    }
}
