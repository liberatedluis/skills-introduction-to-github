import Foundation
import Observation

@MainActor
@Observable
final class CatalogStore {
    var catalog: IndexCatalog?
    var books: [BookMeta] = []
    var error: String?

    private var bookMap: [Int: BookMeta] = [:]

    init() {
        load()
    }

    func load() {
        do {
            books = try Self.decode([BookMeta].self, resource: "books")
            bookMap = Dictionary(uniqueKeysWithValues: books.map { ($0.id, $0) })
            catalog = try Self.decode(IndexCatalog.self, resource: "indexes")
            error = nil
        } catch {
            self.error = error.localizedDescription
        }
    }

    func book(id: Int) -> BookMeta? { bookMap[id] }

    func bookName(_ id: Int) -> String {
        bookMap[id]?.name ?? "Book \(id)"
    }

    func refLabel(book: Int, chapter: Int, verse: Int) -> String {
        "\(bookName(book)) \(chapter):\(verse)"
    }

    func books(testament: String) -> [BookMeta] {
        books.filter { $0.testament == testament }
    }

    private static func decode<T: Decodable>(_ type: T.Type, resource: String) throws -> T {
        guard let url = Bundle.main.url(forResource: resource, withExtension: "json") else {
            throw CatalogError.missing(resource)
        }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(T.self, from: data)
    }
}

enum CatalogError: LocalizedError {
    case missing(String)

    var errorDescription: String? {
        switch self {
        case .missing(let name):
            return "Missing \(name).json in the app bundle."
        }
    }
}
