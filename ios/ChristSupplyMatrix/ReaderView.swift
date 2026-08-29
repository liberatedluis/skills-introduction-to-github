import SwiftUI

struct ReaderView: View {
    @Environment(CatalogStore.self) private var catalog
    @Environment(ScriptureStore.self) private var scripture

    @State private var book: Int
    @State private var chapterNumber: Int
    @State private var highlight: Int
    @State private var lines: [VerseLine] = []
    @State private var loading = false

    init(bookId: Int, chapter: Int, verse: Int) {
        _book = State(initialValue: bookId)
        _chapterNumber = State(initialValue: chapter)
        _highlight = State(initialValue: verse)
    }

    private var bookMeta: BookMeta? { catalog.book(id: book) }
    private var heading: String {
        "\(catalog.bookName(book)) \(chapterNumber)"
    }

    var body: some View {
        VStack(spacing: 0) {
            runningMark
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        Text(heading)
                            .font(MatrixTheme.titleFont)
                            .foregroundStyle(MatrixTheme.gold)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.bottom, 4)
                        Text("\(scripture.title) · \(scripture.copyright)")
                            .font(MatrixTheme.monoFont)
                            .foregroundStyle(MatrixTheme.muted)
                            .padding(.bottom, 16)

                        if loading && lines.isEmpty {
                            ProgressView()
                                .tint(MatrixTheme.accent)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 40)
                        } else if lines.isEmpty {
                            Text(scripture.loadError ?? "This chapter is not in the bundled World English Bible yet.")
                                .font(.subheadline)
                                .foregroundStyle(MatrixTheme.muted)
                                .padding(.vertical, 24)
                        } else {
                            ForEach(lines) { line in
                                verseRow(line)
                                    .id(line.verse)
                            }
                        }

                        LiberateMark()
                        CreditMark()
                    }
                    .padding(.horizontal, 18)
                    .padding(.top, 12)
                    .padding(.bottom, 28)
                }
                .scrollIndicators(.hidden)
                .onChange(of: lines.count) { _, _ in
                    jump(proxy)
                }
                .onAppear { jump(proxy) }
            }
            dock
        }
        .navigationBarTitleDisplayMode(.inline)
        .task(id: "\(book):\(chapterNumber)") {
            await loadChapter()
        }
    }

    private var runningMark: some View {
        HStack {
            Text(Brand.site)
            Spacer()
            Text(Brand.name)
        }
        .font(MatrixTheme.kickerFont)
        .tracking(1.2)
        .foregroundStyle(MatrixTheme.gold)
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(MatrixTheme.bg.opacity(0.92))
        .overlay(alignment: .bottom) {
            Rectangle().fill(MatrixTheme.line).frame(height: 1)
        }
    }

    private var dock: some View {
        HStack(spacing: 10) {
            Button("Prev") { step(-1) }
                .frame(minHeight: 48)
            Button("Next") { step(1) }
                .frame(minHeight: 48)
            Spacer()
            Text("WEB")
                .font(MatrixTheme.kickerFont)
                .foregroundStyle(MatrixTheme.gold)
        }
        .buttonStyle(.bordered)
        .tint(MatrixTheme.accent)
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(MatrixTheme.bg.opacity(0.94))
        .overlay(alignment: .top) {
            Rectangle().fill(MatrixTheme.line).frame(height: 1)
        }
    }

    private func verseRow(_ line: VerseLine) -> some View {
        let active = line.verse == highlight
        return HStack(alignment: .firstTextBaseline, spacing: 12) {
            Text("\(line.verse)")
                .font(.system(.footnote, design: .monospaced).weight(.semibold))
                .foregroundStyle(active ? MatrixTheme.gold : MatrixTheme.muted)
                .frame(width: 28, alignment: .trailing)
                .accessibilityHidden(true)
            Text(line.text)
                .font(MatrixTheme.bodyFont)
                .foregroundStyle(MatrixTheme.fg)
                .shadow(color: MatrixTheme.accent.opacity(0.18), radius: 8, x: 0, y: 0)
                .frame(maxWidth: .infinity, alignment: .leading)
                .textSelection(.enabled)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 8)
        .background(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(active ? MatrixTheme.accent.opacity(0.12) : .clear)
        )
        .overlay {
            if active {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .stroke(MatrixTheme.gold.opacity(0.55), lineWidth: 1)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Verse \(line.verse). \(line.text)")
    }

    private func jump(_ proxy: ScrollViewProxy) {
        guard highlight > 0 else { return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            withAnimation(.easeInOut(duration: 0.25)) {
                proxy.scrollTo(highlight, anchor: .center)
            }
        }
    }

    private func loadChapter() async {
        loading = true
        let loaded = await scripture.ensureChapter(book: book, chapter: chapterNumber)
        lines = loaded
        loading = false
        if highlight < 1 { highlight = 1 }
    }

    private func step(_ delta: Int) {
        guard let meta = bookMeta else { return }
        var nextBook = book
        var nextChapter = chapterNumber + delta
        if nextChapter < 1 {
            if let prev = catalog.books.last(where: { $0.id < book }) {
                nextBook = prev.id
                nextChapter = prev.chapters
            } else {
                return
            }
        } else if nextChapter > meta.chapters {
            if let nxt = catalog.books.first(where: { $0.id > book }) {
                nextBook = nxt.id
                nextChapter = 1
            } else {
                return
            }
        }
        book = nextBook
        chapterNumber = nextChapter
        highlight = 1
    }
}
