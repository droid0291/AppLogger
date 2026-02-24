import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "Security")

struct SecurityDemoView: View {
    @State private var credStatus  = "Tap to log hardcoded credentials."
    @State private var httpStatus  = "Tap to make a cleartext HTTP request."
    @State private var tokenStatus = "Tap to store token in UserDefaults (insecure)."

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {

                // 1. Hardcoded Credentials
                SectionCard(title: "1. Hardcoded Credentials in Logs") {
                    StatusLabel(text: credStatus)
                    ActionButton(label: "Log Credentials") {
                        triggerHardcodedCreds()
                    }
                }

                // 2. Cleartext HTTP
                SectionCard(title: "2. Cleartext HTTP Request") {
                    StatusLabel(text: httpStatus)
                    ActionButton(label: "Make HTTP (not HTTPS) Request") {
                        triggerCleartextHttp()
                    }
                }

                // 3. Token in UserDefaults
                SectionCard(title: "3. Auth Token in UserDefaults") {
                    StatusLabel(text: tokenStatus)
                    HStack(spacing: 12) {
                        ActionButton(label: "Store Token (Insecure)") { storeToken() }
                        ActionButton(label: "Read Token", color: "#444466") { readToken() }
                    }
                }
            }
            .padding(16)
        }
        .background(Color(hex: "#0D0D1A"))
        .navigationTitle("Security Demo")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Hardcoded credentials

    private func triggerHardcodedCreds() {
        // Bug: real credentials appear in OS logs — visible in Console.app and SmartLogger
        let username = "admin"
        let password = "Passw0rd_hardcoded_123!"
        log.error(">>> Security Bug: Logging credentials — username=\(username) password=\(password)")
        credStatus = "❌ Credentials logged:\nusername=\(username)\npassword=\(password)\n\nBug: Secrets visible in system logs."
    }

    // MARK: - Cleartext HTTP

    private func triggerCleartextHttp() {
        httpStatus = "⏳ Making cleartext HTTP request…"
        log.error(">>> Security Bug: Cleartext HTTP request to http://api.example.com (no TLS)")

        // Note: ATS blocks cleartext by default. The log is the bug demonstration.
        // Add NSAllowsArbitraryLoads in Info.plist to actually send it (not done here intentionally).
        Task.detached {
            do {
                let url = URL(string: "http://api.example.com/login")!
                let (_, response) = try await URLSession.shared.data(from: url)
                let code = (response as? HTTPURLResponse)?.statusCode ?? -1
                log.error("Cleartext HTTP response: \(code)")
                await MainActor.run { httpStatus = "HTTP \(code) — cleartext request sent (no TLS!)" }
            } catch {
                // ATS blocks it — log the fact that the code attempted cleartext
                log.error("Cleartext HTTP blocked by ATS: \(error.localizedDescription) — Bug: code should use HTTPS")
                await MainActor.run {
                    httpStatus = "⚠️ Blocked by ATS (App Transport Security)\n\nBug: Code attempted http:// — must use https://"
                }
            }
        }
    }

    // MARK: - Token in UserDefaults

    private func storeToken() {
        let fakeToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.FAKE_PAYLOAD.SIGNATURE"
        UserDefaults.standard.set(fakeToken, forKey: "auth_token")
        log.error(">>> Security Bug: Auth token stored in UserDefaults — NOT encrypted (Keychain should be used)")
        tokenStatus = "❌ Token stored in UserDefaults.\nKey: auth_token\n\nBug: UserDefaults are not encrypted. Use Keychain."
    }

    private func readToken() {
        let token = UserDefaults.standard.string(forKey: "auth_token") ?? "(none)"
        log.error("Security Bug: Reading auth token from UserDefaults: \(token)")
        tokenStatus = "Token read from UserDefaults:\n\(token)"
    }
}
