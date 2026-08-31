import SwiftUI
import UIKit

struct ReaderView: View {
    let docId: String
    let biteId: String

    @Environment(AppModel.self) private var model
    @Environment(\.colorScheme) private var scheme
    @State private var showContents = false
    @State private var copied = false

    var body: some View {
        Group {
            if let found = model.catalog.lookup(docId: docId, biteId: biteId) {
                bitePage(doc: found.0, bite: found.1, index: found.2)
            } else {
                ContentUnavailableView("Missing bite", systemImage: "book.closed")
            }
        }
        .background(CharterTheme.page(for: scheme).ignoresSafeArea())
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showContents) {
            if let doc = model.catalog.document(id: docId) {
                ContentsView(doc: doc, activeBiteId: biteId) { id in
                    showContents = false
                    model.open(docId: doc.id, biteId: id)
                }
            }
        }
        .onAppear { model.remember(docId: docId, biteId: biteId) }
    }

    @ViewBuilder
    private func bitePage(doc: CharterDocument, bite: Bite, index: Int) -> some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Text("\(doc.title) · \(bite.group)")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(CharterTheme.soft(for: scheme))
                        .textCase(.uppercase)
                        .tracking(0.6)
                    Text(bite.cite)
                        .font(.system(.title, design: .serif).weight(.semibold))
                        .foregroundStyle(CharterTheme.text(for: scheme))
                    if !bite.label.isEmpty {
                        Text(bite.label)
                            .font(.system(.title3, design: .serif))
                            .foregroundStyle(CharterTheme.soft(for: scheme))
                    }
                    Text(bite.text)
                        .font(.system(.title3, design: .serif))
                        .foregroundStyle(CharterTheme.text(for: scheme))
                        .lineSpacing(6)
                    if !bite.note.isEmpty {
                        Text(bite.note)
                            .font(.footnote)
                            .foregroundStyle(CharterTheme.soft(for: scheme))
                    }
                    Text("Text: \(doc.sourceLabel). Labels are not the legal text.")
                        .font(.footnote)
                        .foregroundStyle(CharterTheme.soft(for: scheme))
                }
                .padding(22)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .simultaneousGesture(
                DragGesture(minimumDistance: 40).onEnded { value in
                    if value.translation.width < -60 { go(from: doc, index: index, step: 1) }
                    if value.translation.width > 60 { go(from: doc, index: index, step: -1) }
                }
            )

            VStack(spacing: 12) {
                HStack {
                    Text("\(index + 1) of \(doc.bites.count)")
                    Spacer()
                    Text("Where you are")
                }
                .font(.caption)
                .foregroundStyle(CharterTheme.soft(for: scheme))
                ProgressView(value: Double(index + 1), total: Double(doc.bites.count))
                    .tint(CharterTheme.accent(for: scheme))

                HStack(spacing: 8) {
                    pill("Prev", enabled: index > 0 || doc.prevDoc != nil) {
                        go(from: doc, index: index, step: -1)
                    }
                    pill(copied ? "Copied" : "Copy") { copy(doc: doc, bite: bite) }
                    ShareLink(
                        item: shareText(doc: doc, bite: bite),
                        subject: Text("\(bite.cite) · Charter"),
                        message: Text(bite.cite)
                    ) {
                        Text("Share")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .overlay(Capsule().stroke(CharterTheme.soft(for: scheme).opacity(0.35)))
                    }
                    .foregroundStyle(CharterTheme.text(for: scheme))
                    Button(index == doc.bites.count - 1 && doc.nextDoc != nil ? "Continue" : "Next") {
                        go(from: doc, index: index, step: 1)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(index == doc.bites.count - 1 && doc.nextDoc == nil)
                }

                if index == doc.bites.count - 1, let next = doc.nextDoc, let label = doc.nextLabel {
                    Button(label) {
                        model.open(docId: next, biteId: model.catalog.document(id: next)?.bites.first?.id)
                    }
                    .font(.subheadline)
                    .padding(.top, 4)
                }
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 14)
            .background(CharterTheme.raised(for: scheme))
        }
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Home") { model.openHome() }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button("Contents") { showContents = true }
            }
        }
    }

    private func pill(_ title: String, enabled: Bool = true, action: @escaping () -> Void) -> some View {
        Button(title, action: action)
            .disabled(!enabled)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
            .overlay(Capsule().stroke(CharterTheme.soft(for: scheme).opacity(enabled ? 0.35 : 0.15)))
            .foregroundStyle(CharterTheme.text(for: scheme).opacity(enabled ? 1 : 0.4))
    }

    private func go(from doc: CharterDocument, index: Int, step: Int) {
        let next = index + step
        if doc.bites.indices.contains(next) {
            model.open(docId: doc.id, biteId: doc.bites[next].id)
            return
        }
        if step > 0, let nextDoc = doc.nextDoc {
            model.open(docId: nextDoc, biteId: model.catalog.document(id: nextDoc)?.bites.first?.id)
        } else if step < 0, let prevDoc = doc.prevDoc, let prev = model.catalog.document(id: prevDoc) {
            model.open(docId: prev.id, biteId: prev.bites.last?.id)
        }
    }

    private func shareText(doc: CharterDocument, bite: Bite) -> String {
        let web = "https://liberatedluis.github.io/skills-introduction-to-github/charter/#/\(doc.id)/\(bite.id)"
        return "\(bite.text)\n\n— \(doc.title), \(bite.cite)\n\(web)\ncharter://\(doc.id)/\(bite.id)"
    }

    private func copy(doc: CharterDocument, bite: Bite) {
        UIPasteboard.general.string = shareText(doc: doc, bite: bite)
        copied = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) { copied = false }
    }
}
