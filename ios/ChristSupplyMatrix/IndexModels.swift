import Foundation

struct BookMeta: Codable, Identifiable, Hashable {
    let id: Int
    let usfm: String
    let name: String
    let chapters: Int
    let testament: String
}

struct IndexCatalog: Codable {
    let brand: String
    let site: String
    let credit: String
    let edition: String
    let equal: String
    let liberate: String
    let sourceUrl: String
    let shareUrl: String
    let rainbow: [String: PackedIndex]
    let themes: [String: PackedIndex]
    let iam: [NamedVerseList]
    let arcs: [ArcEntry]
    let help: [NamedVerseList]
    let women: [NamedVerseList]
    let men: [NamedVerseList]
    let roots: [RootEntry]
    let dictionary: [DictionaryEntry]
    let wordOfGod: WordOfGod
}

struct PackedIndex: Codable, Identifiable {
    let id: String
    let title: String
    let blurb: String
    let count: Int
    let color: String?
    let versesByBook: [String: [[Int]]]

    var bookIds: [Int] {
        versesByBook.keys.compactMap(Int.init).sorted()
    }

    func verses(in bookId: Int) -> [ChapterVerse] {
        (versesByBook[String(bookId)] ?? []).compactMap { row in
            guard row.count >= 2 else { return nil }
            return ChapterVerse(chapter: row[0], verse: row[1])
        }
    }

    var verseTotal: Int {
        versesByBook.values.reduce(0) { $0 + $1.count }
    }
}

struct NamedVerseList: Codable, Identifiable {
    let id: String
    let title: String
    let note: String?
    let count: Int?
    let verses: [[Int]]

    var passages: [VerseRef] { verses.compactMap(VerseRef.init(packed:)) }
}

struct RootEntry: Codable, Identifiable {
    let id: String
    let title: String
    let roots: String?
    let note: String?
    let verses: [[Int]]

    var passages: [VerseRef] { verses.compactMap(VerseRef.init(packed:)) }
}

struct ArcEntry: Codable, Identifiable {
    let id: String
    let n: Int
    let title: String
    let note: String?
    let verses: [[Int]]

    var passages: [VerseRef] { verses.compactMap(VerseRef.init(packed:)) }
}

struct DictionaryEntry: Codable, Identifiable {
    let id: String
    let n: Int
    let word: String
    let uses: Int
    let note: String
    let letter: String
    let verses: [[Int]]

    var passages: [VerseRef] { verses.compactMap(VerseRef.init(packed:)) }
}

struct WordOfGod: Codable {
    let title: String
    let quote: String
    let entries: [WordOfGodEntry]
}

struct WordOfGodEntry: Codable, Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let book: Int?
    let chapter: Int?
}

struct ChapterVerse: Hashable, Identifiable {
    let chapter: Int
    let verse: Int
    var id: String { "\(chapter):\(verse)" }
}

struct VerseRef: Hashable, Identifiable {
    let book: Int
    let chapter: Int
    let verse: Int

    var id: String { "\(book)-\(chapter)-\(verse)" }

    init(book: Int, chapter: Int, verse: Int) {
        self.book = book
        self.chapter = chapter
        self.verse = verse
    }

    init?(packed: [Int]) {
        if packed.count >= 3 {
            book = packed[0]
            chapter = packed[1]
            verse = packed[2]
        } else {
            return nil
        }
    }
}

struct VerseLine: Identifiable, Hashable {
    let verse: Int
    let text: String
    var id: Int { verse }
}

struct ScriptureBundleFile: Codable {
    let id: String
    let ebibleId: String
    let title: String
    let copyright: String
    let verseCount: Int
    let chapterCount: Int
    let chapters: [String: [VerseAtom]]
}

struct VerseAtom: Codable {
    let verse: Int
    let text: String

    init(from decoder: Decoder) throws {
        var container = try decoder.unkeyedContainer()
        verse = try container.decode(Int.self)
        text = try container.decode(String.self)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.unkeyedContainer()
        try container.encode(verse)
        try container.encode(text)
    }
}

enum IndexCopy {
    static func displayTitle(_ title: String) -> String {
        let trimmed = title.replacingOccurrences(
            of: #"\s+Index$"#,
            with: "",
            options: .regularExpression
        )
        return trimmed.uppercased()
    }

    static func countLabel(_ count: Int, unit: String = "verse") -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        let n = formatter.string(from: NSNumber(value: count)) ?? "\(count)"
        return "\(n) \(unit)\(count == 1 ? "" : "s")"
    }
}
