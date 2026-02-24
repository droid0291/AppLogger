import SwiftUI
import OSLog

private let log = Logger(subsystem: "com.example.SmartLoggerTestApp", category: "UIBug")

struct UIBugDemoView: View {
    @State private var overlapVisible = true
    @State private var truncated = false
    @State private var lowContrast = true
    @State private var imageFixed = false

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {

                // 1. Overlapping views
                SectionCard(title: "1. Overlapping Views") {
                    ZStack(alignment: .topLeading) {
                        RoundedRectangle(cornerRadius: 8).fill(Color(hex: "#1C1C2E"))
                            .frame(height: 80)
                        Text("Checkout Summary")
                            .foregroundColor(.white).padding(10)
                        if overlapVisible {
                            Text("⚠️ BUG: This label overlaps the card")
                                .font(.caption).foregroundColor(.red)
                                .padding(6)
                                .background(Color.black.opacity(0.8))
                                .cornerRadius(6)
                                .offset(x: 12, y: 30)
                        }
                    }
                    ActionButton(label: overlapVisible ? "Hide Overlap (Fix)" : "Show Overlap (Bug)") {
                        overlapVisible.toggle()
                        if overlapVisible {
                            log.warning("UI Bug: Overlapping label re-introduced")
                        } else {
                            log.info("UI Fix: Overlap removed")
                        }
                    }
                }

                // 2. Text Truncation
                SectionCard(title: "2. Text Truncation") {
                    Text("VeryLongUserNameThatDoesNotFitInTheAvailableHorizontalSpaceAndWillOverflowOrBeTruncated")
                        .foregroundColor(.white)
                        .lineLimit(truncated ? 1 : nil)
                        .truncationMode(.tail)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(8)
                        .background(Color(hex: "#2C2C3E"))
                        .cornerRadius(6)
                    ActionButton(label: truncated ? "Remove Truncation (Bug)" : "Apply Truncation (Fix)") {
                        truncated.toggle()
                        if truncated {
                            log.info("UI Fix: lineLimit(1) + truncation applied")
                        } else {
                            log.warning("UI Bug: Long username overflows container — no truncation")
                        }
                    }
                }

                // 3. Low Contrast
                SectionCard(title: "3. Low Contrast (WCAG)") {
                    Button("Submit Payment") {}
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(lowContrast ? Color.white : Color(hex: "#1565C0"))
                        .foregroundColor(lowContrast ? Color(hex: "#EEEEEE") : .white)
                        .cornerRadius(8)
                    ActionButton(label: lowContrast ? "Apply High Contrast (Fix)" : "Apply Low Contrast (Bug)") {
                        lowContrast.toggle()
                        if lowContrast {
                            log.warning("UI Bug: Low-contrast white-on-white button — WCAG fail")
                        } else {
                            log.info("UI Fix: High-contrast button colors applied")
                        }
                    }
                }

                // 4. Missing Image
                SectionCard(title: "4. Missing Image") {
                    ZStack {
                        RoundedRectangle(cornerRadius: 8)
                            .fill(Color(hex: imageFixed ? "#1A237E" : "#222233"))
                            .frame(height: 100)
                        if imageFixed {
                            Image(systemName: "photo.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.white)
                        }
                        // else: blank grey box = the bug
                    }
                    ActionButton(label: imageFixed ? "Remove Image (Bug)" : "Show Placeholder (Fix)") {
                        imageFixed.toggle()
                        if imageFixed {
                            log.info("UI Fix: Placeholder image applied to ImageView")
                        } else {
                            log.warning("UI Bug: ImageView src cleared — blank space visible to user")
                        }
                    }
                }
            }
            .padding(16)
        }
        .background(Color(hex: "#0D0D1A"))
        .navigationTitle("UI Bug Demo")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            log.warning("UI Bug: Overlapping view visible; low contrast button active")
        }
    }
}
