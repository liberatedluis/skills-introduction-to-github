import Foundation
import Observation

@MainActor
@Observable
final class ScriptureStore {
    private(set) var title = Brand.translationTitle
    private(set) var copyright = "public domain"
    private var chapters: [String: [VerseLine]] = [:]
    private var memory = [String: [VerseLine]]()
    var loadError: String?

    init() {
        loadBundle()
    }

    func verses(book: Int, chapter: Int) -> [VerseLine] {
        let key = Self.key(book, chapter)
        if let cached = memory[key] { return cached }
        if let bundled = chapters[key] {
            memory[key] = bundled
            return bundled
        }
        return []
    }

    func hasChapter(book: Int, chapter: Int) -> Bool {
        let key = Self.key(book, chapter)
        return memory[key] != nil || chapters[key] != nil
    }

    func verseText(book: Int, chapter: Int, verse: Int) -> String? {
        verses(book: book, chapter: chapter).first(where: { $0.verse == verse })?.text
    }

    /// Fetches a WEB chapter from getbible when it is not already bundled, then caches it.
    func ensureChapter(book: Int, chapter: Int) async -> [VerseLine] {
        let existing = verses(book: book, chapter: chapter)
        if !existing.isEmpty { return existing }
        let key = Self.key(book, chapter)
        do {
            let fetched = try await Self.fetchRemote(book: book, chapter: chapter)
            if !fetched.isEmpty {
                memory[key] = fetched
                loadError = nil
                return fetched
            }
        } catch {
            loadError = error.localizedDescription
        }
        return []
    }

    private func loadBundle() {
        guard let url = Bundle.main.url(forResource: "web-chapters", withExtension: "json") else {
            loadError = "Missing web-chapters.json in the app bundle."
            return
        }
        do {
            let data = try Data(contentsOf: url)
            let file = try JSONDecoder().decode(ScriptureBundleFile.self, from: data)
            title = file.title
            copyright = file.copyright
            var map: [String: [VerseLine]] = [:]
            map.reserveCapacity(file.chapters.count)
            for (key, atoms) in file.chapters {
                map[key] = atoms.map { VerseLine(verse: $0.verse, text: $0.text) }
            }
            chapters = map
        } catch {
            loadError = error.localizedDescription
        }
    }

    private static func key(_ book: Int, _ chapter: Int) -> String {
        "\(book):\(chapter)"
    }

    private static func fetchRemote(book: Int, chapter: Int) async throws -> [VerseLine] {
        let urls = [
            URL(string: "https://api.getbible.net/v2/web/\(book)/\(chapter).json"),
            URL(string: "https://bolls.life/get-text/WEB/\(book)/\(chapter)/"),
        ].compactMap { $0 }

        var lastError: Error = ScriptureError.unavailable
        for url in urls {
            do {
                let (data, response) = try await URLSession.shared.data(from: url)
                if let http = response as? HTTPURLResponse, http.statusCode >= 400 {
                    throw ScriptureError.http(http.statusCode)
                }
                if let chapterFile = try? JSONDecoder().decode(GetBibleChapter.self, from: data) {
                    let lines = chapterFile.verses.map { VerseLine(verse: $0.verse, text: $0.text) }
                    if !lines.isEmpty { return lines }
                }
                if let rows = try? JSONDecoder().decode([BollsVerse].self, from: data) {
                    let lines = rows.map { VerseLine(verse: $0.verse, text: $0.text) }
                    if !lines.isEmpty { return lines }
                }
            } catch {
                lastError = error
            }
        }
        throw lastError
    }
}

private struct GetBibleChapter: Codable {
    let verses: [GetBibleVerse]
}

private struct GetBibleVerse: Codable {
    let verse: Int
    let text: String
}

private struct BollsVerse: Codable {
    let verse: Int
    let text: String
}

enum ScriptureError: LocalizedError {
    case unavailable
    case http(Int)

    var errorDescription: String? {
        switch self {
        case .unavailable:
            return "World English Bible text is not available for this chapter."
        case .http(let code):
            return "Scripture request failed (\(code))."
        }
    }
}
