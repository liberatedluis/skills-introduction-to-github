import SwiftUI

struct HomeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.colorScheme) private var scheme

    var body: some View {
        @Bindable var model = model
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text("Three founding texts. One thought at a time.")
                    .font(.system(.largeTitle, design: .serif))
                    .foregroundStyle(CharterTheme.text(for: scheme))
                Text("A quiet civic reader of the Declaration, the Constitution, and the Bill of Rights. Free. Offline. No ads, accounts, or tracking.")
                    .font(.system(.body, design: .serif))
                    .foregroundStyle(CharterTheme.soft(for: scheme))

                VStack(spacing: 12) {
                    ForEach(model.catalog.homeDocuments) { doc in
                        Button {
                            model.open(docId: doc.id, biteId: doc.bites.first?.id)
                        } label: {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("\(doc.year)  ·  \(doc.bites.count) bites")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(CharterTheme.soft(for: scheme))
                                    .textCase(.uppercase)
                                    .tracking(0.8)
                                Text(doc.title)
                                    .font(.system(.title3, design: .serif).weight(.semibold))
                                    .foregroundStyle(CharterTheme.text(for: scheme))
                                    .multilineTextAlignment(.leading)
                                Text(doc.blurb)
                                    .font(.system(.subheadline, design: .serif))
                                    .foregroundStyle(CharterTheme.soft(for: scheme))
                                    .multilineTextAlignment(.leading)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(16)
                            .background(CharterTheme.raised(for: scheme), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                            .overlay(
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .stroke(CharterTheme.soft(for: scheme).opacity(0.25), lineWidth: 1)
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }

                if let last = model.lastBite, let found = model.catalog.lookup(docId: last.docId, biteId: last.biteId) {
                    Button("Continue · \(found.0.short), \(found.1.cite)") {
                        model.open(docId: last.docId, biteId: last.biteId)
                    }
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(CharterTheme.accent(for: scheme))
                }

                Button("Later amendments XI–XXVII, so the Constitution is whole.") {
                    model.open(docId: "later", biteId: "11")
                }
                .font(.subheadline)
                .foregroundStyle(CharterTheme.accent(for: scheme))

                NavigationLink("Light and dark PDFs", value: Screen.pdfs)
                    .font(.subheadline.weight(.medium))

                VStack(spacing: 6) {
                    Text("Created by Christ Supply")
                    Link("Support Here", destination: URL(string: "https://christ.supply/support-us")!)
                }
                .font(.footnote)
                .foregroundStyle(CharterTheme.soft(for: scheme))
                .frame(maxWidth: .infinity)
                .padding(.top, 12)
            }
            .padding(22)
        }
        .background(CharterTheme.page(for: scheme).ignoresSafeArea())
        .navigationTitle("Charter")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                VStack(spacing: 0) {
                    Text("Charter").font(.system(.headline, design: .serif))
                    Text("Civic reader").font(.caption2).foregroundStyle(.secondary)
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Picker("Theme", selection: $model.theme) {
                        ForEach(ThemePreference.allCases) { preference in
                            Text(preference.title).tag(preference)
                        }
                    }
                } label: {
                    Text(model.theme == .dark ? "Light" : "Dark")
                }
            }
        }
    }
}
