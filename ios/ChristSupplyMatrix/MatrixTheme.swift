import SwiftUI

enum Brand {
    static let name = "Christ Supply Holy Bible"
    static let site = "ChristSupply.Net"
    static let siteURL = URL(string: "https://christsupply.net")!
    static let credit = "Made by Liberated Luis With Cursor, Claude Opus, and MacBook"
    static let equal = "All Users Are Created Equally By God"
    static let liberate = "LIBERA OMNES UTENTES | LIBERATE ALL USERS"
    static let edition = "WEB Protestant Edition - Public Domain"
    static let translationTitle = "World English Bible"
}

enum MatrixTheme {
    static let bg = Color(red: 0x02 / 255, green: 0x04 / 255, blue: 0x02 / 255)
    static let bg2 = Color(red: 0x07 / 255, green: 0x14 / 255, blue: 0x0A / 255)
    static let fg = Color(red: 0xC8 / 255, green: 0xFF / 255, blue: 0xD4 / 255)
    static let muted = Color(red: 0x6E / 255, green: 0xA8 / 255, blue: 0x7A / 255)
    static let accent = Color(red: 0x7C / 255, green: 0xFF / 255, blue: 0x9A / 255)
    static let gold = Color(red: 0xE8 / 255, green: 0xFF / 255, blue: 0x8A / 255)
    static let line = Color(red: 0x7C / 255, green: 0xFF / 255, blue: 0x9A / 255).opacity(0.22)

    static let titleFont = Font.system(.title2, design: .default).weight(.bold)
    static let headlineFont = Font.system(.headline, design: .default).weight(.semibold)
    static let bodyFont = Font.system(.body, design: .serif)
    static let monoFont = Font.system(.caption, design: .monospaced).weight(.medium)
    static let kickerFont = Font.system(.caption2, design: .monospaced).weight(.semibold)

    static let rainbowOrder = ["red", "orange", "gold", "yellow", "green", "cyan", "blue", "purple", "pink"]

    static let themeGroups: [(label: String, ids: [String])] = [
        ("WHITE", ["iam", "lord-said", "arcs"]),
        ("NOW", ["afraid", "help", "mercy"]),
        ("LIFE", ["believe", "love", "peace", "sin", "wrath"]),
    ]

    static func color(hex: String?) -> Color? {
        guard var value = hex?.trimmingCharacters(in: .whitespacesAndNewlines), !value.isEmpty else { return nil }
        if value.hasPrefix("#") { value.removeFirst() }
        guard value.count == 6, let int = UInt64(value, radix: 16) else { return nil }
        return Color(
            red: Double((int >> 16) & 0xFF) / 255,
            green: Double((int >> 8) & 0xFF) / 255,
            blue: Double(int & 0xFF) / 255
        )
    }
}

struct MatrixBackground: View {
    var body: some View {
        ZStack {
            RadialGradient(
                colors: [MatrixTheme.bg2, MatrixTheme.bg],
                center: .top,
                startRadius: 20,
                endRadius: 720
            )
            Canvas { context, size in
                let step: CGFloat = 3
                var y: CGFloat = 0
                while y < size.height {
                    let rect = CGRect(x: 0, y: y + 2, width: size.width, height: 1)
                    context.fill(Path(rect), with: .color(.black.opacity(0.18)))
                    y += step
                }
            }
            .allowsHitTesting(false)
            .opacity(0.35)
        }
        .ignoresSafeArea()
    }
}

extension Color {
    static let matrixAccent = MatrixTheme.accent
}
