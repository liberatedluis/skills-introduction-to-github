import SwiftUI

@main
struct CharterApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(model)
                .preferredColorScheme(model.theme.colorScheme)
                .onOpenURL { model.open(url: $0) }
        }
    }
}

struct ContentView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        NavigationStack(path: $model.path) {
            HomeView()
                .navigationDestination(for: Screen.self) { screen in
                    switch screen {
                    case .reader(let docId, let biteId):
                        ReaderView(docId: docId, biteId: biteId)
                            .id("\(docId)/\(biteId)")
                    case .pdfs:
                        PDFLibraryView()
                    }
                }
        }
        .tint(CharterTheme.accent(for: model.theme.resolved))
    }
}
