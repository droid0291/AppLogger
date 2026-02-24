import SwiftUI

// ─────────────────────────────────────────────────────────────────────────────
// DemoPage — wraps a list of DemoItem buttons with a standard chrome
// ─────────────────────────────────────────────────────────────────────────────

struct DemoItem {
    let label: String
    let description: String
    let color: String
    let action: () -> Void
}

struct DemoPage: View {
    let title: String
    let items: [DemoItem]
    var footerNote: String = ""

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                ForEach(items.indices, id: \.self) { i in
                    let item = items[i]
                    SectionCard(title: item.label) {
                        Text(item.description)
                            .font(.system(size: 13))
                            .foregroundColor(Color(hex: "#9090B0"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        ActionButton(label: "Trigger", color: item.color) {
                            item.action()
                        }
                    }
                }
                if !footerNote.isEmpty {
                    Text(footerNote)
                        .font(.system(size: 13))
                        .foregroundColor(Color(hex: "#9090B0"))
                        .multilineTextAlignment(.center)
                        .padding(.top, 8)
                }
            }
            .padding(16)
        }
        .background(Color(hex: "#0D0D1A"))
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SectionCard — dark card container
// ─────────────────────────────────────────────────────────────────────────────

struct SectionCard<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(Color(hex: "#9090B0"))
                .textCase(.uppercase)
            content()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(hex: "#1C1C2E"))
        .cornerRadius(14)
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color(hex: "#2E2E44"), lineWidth: 1))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// ActionButton — styled pill button
// ─────────────────────────────────────────────────────────────────────────────

struct ActionButton: View {
    let label: String
    var color: String = "#4F6EF7"
    var disabled: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(label)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
                .background(disabled ? Color(hex: "#333355") : Color(hex: color))
                .cornerRadius(8)
        }
        .disabled(disabled)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// StatusLabel — multiline status readout
// ─────────────────────────────────────────────────────────────────────────────

struct StatusLabel: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.system(size: 13, design: .monospaced))
            .foregroundColor(.white)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(10)
            .background(Color(hex: "#0D0D1A"))
            .cornerRadius(6)
            .fixedSize(horizontal: false, vertical: true)
    }
}
