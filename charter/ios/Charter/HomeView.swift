import SwiftUI

struct HomeView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.colorScheme) private var scheme

    var body: some View {
        @Bindable var model = model
        VStack(alignment: .leading, spacing: 8) {
            Text("Three founding texts. One thought at a time.")
                .font(.system(.title3, design: .serif))
                .foregroundStyle(CharterTheme.text(for: scheme))
                .fixedSize(horizontal: false, vertical: true)

            VStack(spacing: 8) {
                ForEach(model.catalog.homeDocuments) { doc in
                    Button {
                        model.open(docId: doc.id, biteId: doc.bites.first?.id)
                    } label: {
                        VStack(alignment: .leading, spacing: 3) {
                            Text("\(doc.year)  ·  \(doc.bites.count) bites")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(CharterTheme.soft(for: scheme))
                                .textCase(.uppercase)
                                .tracking(0.6)
                            Text(doc.title)
                                .font(.system(.headline, design: .serif).weight(.semibold))
                                .foregroundStyle(CharterTheme.text(for: scheme))
                                .multilineTextAlignment(.leading)
                                .lineLimit(2)
                                .minimumScaleFactor(0.85)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(CharterTheme.raised(for: scheme), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(CharterTheme.soft(for: scheme).opacity(0.25), lineWidth: 1)
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .frame(maxHeight: .infinity)

            if let last = model.lastBite, let found = model.catalog.lookup(docId: last.docId, biteId: last.biteId) {
                Button("Continue · \(found.0.short), \(found.1.cite)") {
                    model.open(docId: last.docId, biteId: last.biteId)
                }
                .font(.footnote.weight(.medium))
                .foregroundStyle(CharterTheme.accent(for: scheme))
            }

            Button("Later amendments XI–XXVII, so the Constitution is whole.") {
                model.open(docId: "later", biteId: "11")
            }
            .font(.footnote)
            .foregroundStyle(CharterTheme.accent(for: scheme))
            .lineLimit(2)
            .minimumScaleFactor(0.85)

            HStack(spacing: 4) {
                Text("Created by Christ Supply,")
                Link("Support Here", destination: URL(string: "https://christ.supply/support-us")!)
            }
            .font(.caption)
            .foregroundStyle(CharterTheme.soft(for: scheme))
            .frame(maxWidth: .infinity)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(CharterTheme.page(for: scheme).ignoresSafeArea())
        .navigationTitle("Charter")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                VStack(spacing: 0) {
                    Text("Charter").font(.system(.headline, design: .serif))
                    Text("One thought at a time").font(.caption2).foregroundStyle(.secondary)
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
