import PDFKit
import SwiftUI

struct PDFLibraryView: View {
    @Environment(\.colorScheme) private var scheme
    @State private var edition: Edition = .light

    enum Edition: String, CaseIterable, Identifiable {
        case light
        case dark
        var id: String { rawValue }
        var title: String { self == .light ? "Light PDF" : "Dark PDF" }
        var resource: String { self == .light ? "charter-light" : "charter-dark" }
    }

    var body: some View {
        VStack(spacing: 0) {
            Picker("Edition", selection: $edition) {
                ForEach(Edition.allCases) { item in
                    Text(item.title).tag(item)
                }
            }
            .pickerStyle(.segmented)
            .padding()
            PDFKitView(resource: edition.resource)
                .background(CharterTheme.page(for: scheme))
        }
        .navigationTitle("Charter PDFs")
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
