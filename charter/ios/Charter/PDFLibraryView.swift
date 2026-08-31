import PDFKit
import SwiftUI

struct PDFBook: Identifiable, Hashable {
    let id: String
    let title: String
    let resourcePrefix: String
}

struct PDFLibraryView: View {
    @Environment(\.colorScheme) private var scheme
    @State private var book: PDFBook = PDFLibraryView.books[0]
    @State private var edition: Edition = .light

    static let books: [PDFBook] = [
        PDFBook(id: "charter", title: "Charter (all three)", resourcePrefix: "charter"),
        PDFBook(id: "declaration", title: "Declaration", resourcePrefix: "declaration"),
        PDFBook(id: "constitution", title: "Constitution", resourcePrefix: "constitution"),
        PDFBook(id: "rights", title: "Bill of Rights and later amendments", resourcePrefix: "rights"),
    ]

    enum Edition: String, CaseIterable, Identifiable {
        case light
        case dark
        var id: String { rawValue }
        var title: String { self == .light ? "Light" : "Dark" }
    }

    var body: some View {
        VStack(spacing: 0) {
            Picker("Book", selection: $book) {
                ForEach(Self.books) { item in
                    Text(item.title).tag(item)
                }
            }
            .pickerStyle(.menu)
            .padding([.horizontal, .top])
            Picker("Edition", selection: $edition) {
                ForEach(Edition.allCases) { item in
                    Text(item.title).tag(item)
                }
            }
            .pickerStyle(.segmented)
            .padding()
            PDFKitView(resource: "\(book.resourcePrefix)-\(edition.rawValue)")
                .background(CharterTheme.page(for: scheme))
        }
        .navigationTitle("The whole library")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            edition = scheme == .dark ? .dark : .light
        }
    }
}

struct PDFKitView: UIViewRepresentable {
    let resource: String

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.displayMode = .singlePageContinuous
        view.displayDirection = .vertical
        load(into: view)
        return view
    }

    func updateUIView(_ view: PDFView, context: Context) {
        load(into: view)
    }

    private func load(into view: PDFView) {
        if let url = Bundle.main.url(forResource: resource, withExtension: "pdf") {
            view.document = PDFDocument(url: url)
        }
    }
}
