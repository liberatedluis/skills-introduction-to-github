import Foundation

struct Catalog: Sendable {
    let documents: [CharterDocument]
    let homeIds: [String]

    var homeDocuments: [CharterDocument] {
        homeIds.compactMap(document(id:))
    }

    func document(id: String) -> CharterDocument? {
        documents.first { $0.id == id }
    }

    func lookup(docId: String, biteId: String) -> (CharterDocument, Bite, Int)? {
        guard let doc = document(id: docId), let index = doc.bites.firstIndex(where: { $0.id == biteId }) else {
            return nil
        }
        return (doc, doc.bites[index], index)
    }

    static func load() -> Catalog {
        guard
            let url = Bundle.main.url(forResource: "texts", withExtension: "json"),
            let data = try? Data(contentsOf: url),
            let bundle = try? JSONDecoder().decode(TextBundle.self, from: data)
        else {
            fatalError("Charter texts.json is missing from the app bundle.")
        }
        return Catalog(documents: bundle.documents, homeIds: bundle.homeIds)
    }
}

private struct TextBundle: Decodable {
    let documents: [CharterDocument]
    let homeIds: [String]
}

struct CharterDocument: Decodable, Identifiable, Hashable {
    let id: String
    let title: String
    let short: String
    let year: String
    let blurb: String
    let source: String
    let sourceLabel: String
    let nextDoc: String?
    let nextLabel: String?
    let prevDoc: String?
    let bites: [Bite]
}

struct Bite: Decodable, Identifiable, Hashable {
    let id: String
    let kind: String
    let group: String
    let cite: String
    let label: String
    let text: String
    let note: String
}
