import SwiftUI
import UIKit

enum Screen: Hashable {
    case reader(docId: String, biteId: String)
    case pdfs
}

enum ThemePreference: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var title: String {
        switch self {
        case .system: "System"
        case .light: "Light"
        case .dark: "Dark"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system: nil
        case .light: .light
        case .dark: .dark
        }
    }

    var resolved: ColorScheme {
        colorScheme ?? (UITraitCollection.current.userInterfaceStyle == .dark ? .dark : .light)
    }
}

@MainActor
@Observable
final class AppModel {
    let catalog: Catalog
    var path: [Screen] = []
    var theme: ThemePreference {
        didSet { UserDefaults.standard.set(theme.rawValue, forKey: "charter-theme") }
    }

    init() {
        catalog = Catalog.load()
        let stored = UserDefaults.standard.string(forKey: "charter-theme") ?? ""
        theme = ThemePreference(rawValue: stored) ?? .system
    }

    var lastBite: (docId: String, biteId: String)? {
        guard
            let docId = UserDefaults.standard.string(forKey: "charter-last-doc"),
            let biteId = UserDefaults.standard.string(forKey: "charter-last-bite"),
            catalog.lookup(docId: docId, biteId: biteId) != nil
        else { return nil }
        return (docId, biteId)
    }

    func openHome() {
        path.removeAll()
    }

    func open(docId: String, biteId: String?) {
        guard let doc = catalog.document(id: docId) else { return }
        let id = biteId.flatMap { raw in doc.bites.contains(where: { $0.id == raw }) ? raw : nil } ?? doc.bites[0].id
        remember(docId: doc.id, biteId: id)
        path = [.reader(docId: doc.id, biteId: id)]
    }

    func open(url: URL) {
        let parts = url.pathComponents.filter { $0 != "/" }
        let host = url.host
        let docId = host ?? parts.first
        let biteId = host == nil ? parts.dropFirst().first : parts.first
        guard let docId else { return }
        open(docId: docId, biteId: biteId)
    }

    func remember(docId: String, biteId: String) {
        UserDefaults.standard.set(docId, forKey: "charter-last-doc")
        UserDefaults.standard.set(biteId, forKey: "charter-last-bite")
    }
}

enum CharterTheme {
    static let parchment = Color(red: 0.953, green: 0.918, blue: 0.847)
    static let ink = Color(red: 0.165, green: 0.133, blue: 0.094)
    static let raisedLight = Color(red: 0.980, green: 0.965, blue: 0.922)
    static let raisedDark = Color(red: 0.129, green: 0.110, blue: 0.090)
    static let brown = Color(red: 0.427, green: 0.231, blue: 0.133)
    static let gold = Color(red: 0.878, green: 0.710, blue: 0.478)

    static func page(for scheme: ColorScheme) -> Color {
        scheme == .dark ? ink : parchment
    }

    static func raised(for scheme: ColorScheme) -> Color {
        scheme == .dark ? raisedDark : raisedLight
    }

    static func text(for scheme: ColorScheme) -> Color {
        scheme == .dark ? Color(red: 0.933, green: 0.894, blue: 0.824) : ink
    }

    static func soft(for scheme: ColorScheme) -> Color {
        scheme == .dark ? Color(red: 0.718, green: 0.667, blue: 0.588) : Color(red: 0.369, green: 0.325, blue: 0.282)
    }

    static func accent(for scheme: ColorScheme) -> Color {
        scheme == .dark ? gold : brown
    }
}
