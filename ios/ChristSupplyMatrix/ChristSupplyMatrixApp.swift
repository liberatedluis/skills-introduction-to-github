import SwiftUI

@main
struct ChristSupplyMatrixApp: App {
    @State private var catalog = CatalogStore()
    @State private var scripture = ScriptureStore()

    var body: some Scene {
        WindowGroup {
            RootContainer()
                .environment(catalog)
                .environment(scripture)
                .preferredColorScheme(.dark)
                .tint(MatrixTheme.accent)
        }
    }
}

struct RootContainer: View {
    @Environment(CatalogStore.self) private var catalog
    @State private var path: [Destination] = []

    var body: some View {
        NavigationStack(path: $path) {
            Group {
                if let error = catalog.error {
                    CatalogErrorView(message: error)
                } else if catalog.catalog == nil {
                    ProgressView()
                        .tint(MatrixTheme.accent)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    IndexPageView(path: [], navigationPath: $path)
                }
            }
            .matrixChrome(showBack: false, navigationPath: $path)
            .navigationDestination(for: Destination.self) { destination in
                switch destination {
                case .page(let parts):
                    IndexPageView(path: parts, navigationPath: $path)
                        .matrixChrome(showBack: true, navigationPath: $path)
                case .passage(let book, let chapter, let verse):
                    ReaderView(bookId: book, chapter: chapter, verse: verse)
                        .matrixChrome(showBack: true, navigationPath: $path)
                }
            }
        }
        .background(MatrixBackground())
    }
}

enum Destination: Hashable {
    case page([String])
    case passage(book: Int, chapter: Int, verse: Int)
}

private struct CatalogErrorView: View {
    let message: String

    var body: some View {
        VStack(spacing: 12) {
            Text("Index catalog missing")
                .font(MatrixTheme.titleFont)
                .foregroundStyle(MatrixTheme.gold)
            Text(message)
                .font(MatrixTheme.bodyFont)
                .foregroundStyle(MatrixTheme.muted)
                .multilineTextAlignment(.center)
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
