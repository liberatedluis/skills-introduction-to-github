import SwiftUI

struct IndexPageView: View {
    let path: [String]
    @Binding var navigationPath: [Destination]
    @Environment(CatalogStore.self) private var catalog

    var body: some View {
        Group {
            if let data = catalog.catalog {
                IndexSheet {
                    pageBody(data)
                }
            } else {
                ProgressView().tint(MatrixTheme.accent)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private func pageBody(_ data: IndexCatalog) -> some View {
        let root = path.first ?? ""
        if root.isEmpty {
            RootIndexView(data: data, open: open)
        } else if root == "word" {
            WordOfGodView(data: data, open: open, openPassage: openPassage)
        } else if root == "ot" {
            TestamentView(title: "Old Testament", blurb: "Genesis through Malachi, linked into each book’s chapter index.", testament: "OT", open: open)
        } else if root == "nt" {
            TestamentView(title: "New Testament", blurb: "Matthew through Revelation, linked into each book’s chapter index.", testament: "NT", open: open)
        } else if root == "library" {
            LibraryView(bookId: path.dropFirst().first.flatMap(Int.init), open: open, openPassage: openPassage)
        } else if let packed = data.rainbow[root] ?? data.themes[root] {
            PackedIndexView(row: packed, bookId: path.dropFirst().first.flatMap(Int.init), open: open, openPassage: openPassage)
        } else if root == "iam" {
            ListIndexView(title: "I AM THE LORD", blurb: "116 names and titles — tap one to open its Scriptures.", items: data.iam.map { ListCardItem(id: $0.id, title: $0.title, subtitle: $0.note, extra: $0.count.map { IndexCopy.countLabel($0) }, roots: nil, passages: $0.passages) }, selected: path.dropFirst().first, base: "iam", open: open, openPassage: openPassage)
        } else if root == "help" {
            ListIndexView(title: "Help Me Now God", blurb: "Short hope for this moment — 8 paths.", items: data.help.map { ListCardItem(id: $0.id, title: $0.title, subtitle: $0.note, extra: nil, roots: nil, passages: $0.passages) }, selected: path.dropFirst().first, base: "help", open: open, openPassage: openPassage)
        } else if root == "women" {
            ListIndexView(title: "Women of God", blurb: "Courage, faith, and faithfulness.", items: data.women.map { ListCardItem(id: $0.id, title: $0.title, subtitle: $0.note, extra: nil, roots: nil, passages: $0.passages) }, selected: path.dropFirst().first, base: "women", open: open, openPassage: openPassage)
        } else if root == "men" {
            ListIndexView(title: "Men of God", blurb: "Faith, repentance, and courage.", items: data.men.map { ListCardItem(id: $0.id, title: $0.title, subtitle: $0.note, extra: nil, roots: nil, passages: $0.passages) }, selected: path.dropFirst().first, base: "men", open: open, openPassage: openPassage)
        } else if root == "roots" {
            ListIndexView(title: "Word Roots", blurb: "66 core words with Hebrew / Aramaic / Greek roots.", items: data.roots.map { ListCardItem(id: $0.id, title: $0.title, subtitle: $0.note, extra: nil, roots: $0.roots, passages: $0.passages) }, selected: path.dropFirst().first, base: "roots", open: open, openPassage: openPassage)
        } else if root == "words" {
            DictionaryView(data: data, letter: path.count > 1 ? path[1] : nil, wordId: path.count > 2 ? path[2] : nil, open: open, openPassage: openPassage)
        } else if root == "arcs" {
            ArcsView(data: data, group: path.count > 1 ? path[1] : nil, arcId: path.count > 2 ? path[2] : nil, open: open, openPassage: openPassage)
        } else {
            Text("Unknown index.")
                .foregroundStyle(MatrixTheme.muted)
                .frame(maxWidth: .infinity)
        }
    }

    private func open(_ parts: [String]) {
        navigationPath.append(.page(parts))
    }

    private func openPassage(book: Int, chapter: Int, verse: Int) {
        navigationPath.append(.passage(book: book, chapter: chapter, verse: verse))
    }
}

private struct RootIndexView: View {
    let data: IndexCatalog
    let open: ([String]) -> Void

    var body: some View {
        VStack(spacing: 4) {
            VStack(spacing: 6) {
                Text("C H R I S T . S U P P L Y")
                    .font(MatrixTheme.kickerFont)
                    .tracking(3)
                    .foregroundStyle(MatrixTheme.fg)
                Text("Root Index")
                    .font(MatrixTheme.titleFont)
                    .foregroundStyle(MatrixTheme.fg)
                Text("Go to the Word, the rainbow letters, and the clickable study indexes from the offline WEB packet.")
                    .font(.subheadline)
                    .foregroundStyle(MatrixTheme.muted)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding(.bottom, 8)

            Kicker(text: "WORD")
            IndexCard(title: "THE WORD OF GOD", subtitle: "In the beginning") { open(["word"]) }
            IndexCard(title: "OLD TESTAMENT", subtitle: "Genesis through Malachi") { open(["ot"]) }
            IndexCard(title: "NEW TESTAMENT", subtitle: "Matthew through Revelation") { open(["nt"]) }

            Kicker(text: "RAINBOW")
            ForEach(MatrixTheme.rainbowOrder, id: \.self) { id in
                if let row = data.rainbow[id] {
                    IndexCard(
                        title: IndexCopy.displayTitle(row.title),
                        subtitle: IndexCopy.countLabel(row.count),
                        color: MatrixTheme.color(hex: row.color)
                    ) { open([id]) }
                }
            }

            ForEach(MatrixTheme.themeGroups, id: \.label) { group in
                Kicker(text: group.label)
                ForEach(group.ids, id: \.self) { id in
                    themeCard(id)
                }
            }

            Kicker(text: "PEOPLE")
            IndexCard(title: "WOMEN OF GOD", subtitle: "\(data.women.count) people") { open(["women"]) }
            IndexCard(title: "MEN OF GOD", subtitle: "\(data.men.count) people") { open(["men"]) }

            Kicker(text: "WORDS")
            IndexCard(title: "WORD INDEX", subtitle: "\(data.dictionary.count) words") { open(["words"]) }
            IndexCard(title: "WORD ROOTS", subtitle: "\(data.roots.count) core words") { open(["roots"]) }
        }
    }

    @ViewBuilder
    private func themeCard(_ id: String) -> some View {
        if id == "iam" {
            IndexCard(title: "I AM THE LORD", subtitle: "116 names and titles — tap one to open its Scriptures.") { open(["iam"]) }
        } else if id == "arcs" {
            IndexCard(title: "ARCS OF GOD", subtitle: "\(data.arcs.count) arcs") { open(["arcs"]) }
        } else if id == "help" {
            IndexCard(title: "HELP ME NOW GOD", subtitle: "Short hope for this moment — 8 paths.") { open(["help"]) }
        } else if let row = data.themes[id] {
            IndexCard(title: IndexCopy.displayTitle(row.title), subtitle: row.blurb) { open([id]) }
        }
    }
}

private struct WordOfGodView: View {
    let data: IndexCatalog
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            heading("The Word of God", subtitle: "“\(data.wordOfGod.quote)”")
            ForEach(data.wordOfGod.entries) { row in
                if row.id == "library" {
                    IndexCard(title: row.title, subtitle: row.subtitle) { open(["library"]) }
                } else if let book = row.book, let chapter = row.chapter {
                    IndexCard(title: row.title, subtitle: row.subtitle) {
                        openPassage(book, chapter, 1)
                    }
                }
            }
        }
    }
}

private struct TestamentView: View {
    @Environment(CatalogStore.self) private var catalog
    let title: String
    let blurb: String
    let testament: String
    let open: ([String]) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            heading(title, subtitle: blurb)
            ForEach(catalog.books(testament: testament)) { book in
                IndexCard(title: book.name, subtitle: "\(book.chapters) chapters") {
                    open(["library", String(book.id)])
                }
            }
        }
    }
}

private struct LibraryView: View {
    @Environment(CatalogStore.self) private var catalog
    let bookId: Int?
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    var body: some View {
        if let bookId, let book = catalog.book(id: bookId) {
            VStack(alignment: .leading, spacing: 8) {
                heading(book.name, subtitle: "\(book.chapters) chapters · tap to open in the Matrix reader")
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 88), spacing: 8)], spacing: 8) {
                    ForEach(1...book.chapters, id: \.self) { chapter in
                        LetterChip(title: "\(chapter)") {
                            openPassage(book.id, chapter, 1)
                        }
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 8) {
                heading("Full Library", subtitle: "All books, chapters, and indexes.")
                IndexCard(title: "Old Testament", subtitle: "Genesis through Malachi") { open(["ot"]) }
                IndexCard(title: "New Testament", subtitle: "Matthew through Revelation") { open(["nt"]) }
                ForEach(catalog.books) { book in
                    IndexCard(title: book.name, subtitle: "\(book.chapters) chapters") {
                        open(["library", String(book.id)])
                    }
                }
            }
        }
    }
}

private struct PackedIndexView: View {
    @Environment(CatalogStore.self) private var catalog
    let row: PackedIndex
    let bookId: Int?
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    var body: some View {
        if let bookId {
            VStack(alignment: .leading, spacing: 8) {
                heading(catalog.bookName(bookId), subtitle: row.title)
                ForEach(row.verses(in: bookId)) { pair in
                    VerseChip(label: catalog.refLabel(book: bookId, chapter: pair.chapter, verse: pair.verse)) {
                        openPassage(bookId, pair.chapter, pair.verse)
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 8) {
                heading(row.title, subtitle: "\(row.blurb) \(IndexCopy.countLabel(row.verseTotal)) linked.", color: MatrixTheme.color(hex: row.color))
                ForEach(row.bookIds, id: \.self) { id in
                    let n = row.verses(in: id).count
                    IndexCard(title: catalog.bookName(id), subtitle: IndexCopy.countLabel(n)) {
                        open([row.id, String(id)])
                    }
                }
            }
        }
    }
}

struct ListCardItem: Identifiable {
    let id: String
    let title: String
    let subtitle: String?
    let extra: String?
    let roots: String?
    let passages: [VerseRef]
}

private struct ListIndexView: View {
    @Environment(CatalogStore.self) private var catalog
    let title: String
    let blurb: String
    let items: [ListCardItem]
    let selected: String?
    let base: String
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    var body: some View {
        if let selected, let row = items.first(where: { $0.id == selected }) {
            VStack(alignment: .leading, spacing: 8) {
                heading(row.title, subtitle: row.subtitle ?? blurb)
                if let roots = row.roots, !roots.isEmpty {
                    Text(roots)
                        .font(.system(.subheadline, design: .monospaced))
                        .foregroundStyle(MatrixTheme.muted)
                        .frame(maxWidth: .infinity)
                        .multilineTextAlignment(.center)
                }
                ForEach(row.passages) { ref in
                    VerseChip(label: catalog.refLabel(book: ref.book, chapter: ref.chapter, verse: ref.verse)) {
                        openPassage(ref.book, ref.chapter, ref.verse)
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 8) {
                heading(title, subtitle: blurb)
                ForEach(items) { row in
                    let sub = row.roots ?? row.extra ?? row.subtitle ?? IndexCopy.countLabel(row.passages.count)
                    IndexCard(title: row.title, subtitle: sub) {
                        open([base, row.id])
                    }
                }
            }
        }
    }
}

private struct DictionaryView: View {
    @Environment(CatalogStore.self) private var catalog
    let data: IndexCatalog
    let letter: String?
    let wordId: String?
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    private var letters: [String] {
        let set = Set(data.dictionary.map(\.letter).filter { $0.range(of: #"^[A-Z]$"#, options: .regularExpression) != nil })
        return set.sorted()
    }

    var body: some View {
        if let letter {
            let rows = data.dictionary.filter { $0.letter == letter }
            if let wordId, let row = rows.first(where: { $0.id == wordId }) ?? data.dictionary.first(where: { $0.id == wordId }) {
                VStack(alignment: .leading, spacing: 8) {
                    heading(String(format: "%04d. %@", row.n, row.word), subtitle: row.note)
                    Text("Appears \(IndexCopy.countLabel(row.uses, unit: "time")) in this WEB edition. Tap a verse to jump into the Word.")
                        .font(.subheadline)
                        .foregroundStyle(MatrixTheme.muted)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity)
                    ForEach(row.passages) { ref in
                        VerseChip(label: catalog.refLabel(book: ref.book, chapter: ref.chapter, verse: ref.verse)) {
                            openPassage(ref.book, ref.chapter, ref.verse)
                        }
                    }
                }
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    heading("\(letter) Word Index", subtitle: "\(rows.count) words")
                    ForEach(rows) { row in
                        IndexCard(title: row.word, subtitle: IndexCopy.countLabel(row.uses, unit: "use")) {
                            open(["words", letter, row.id])
                        }
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 8) {
                heading("Word Index", subtitle: "Bible words with meaning notes. See also Word Roots.")
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 64), spacing: 8)], spacing: 8) {
                    ForEach(letters, id: \.self) { item in
                        let n = data.dictionary.filter { $0.letter == item }.count
                        LetterChip(title: item, count: n) { open(["words", item]) }
                    }
                }
            }
        }
    }
}

private struct ArcsView: View {
    @Environment(CatalogStore.self) private var catalog
    let data: IndexCatalog
    let group: String?
    let arcId: String?
    let open: ([String]) -> Void
    let openPassage: (Int, Int, Int) -> Void

    var body: some View {
        if let group {
            let bounds = group.split(separator: "-").compactMap { Int($0) }
            let start = bounds.first ?? 1
            let end = bounds.dropFirst().first ?? start
            let rows = data.arcs.filter { $0.n >= start && $0.n <= end }
            if let arcId, let row = data.arcs.first(where: { $0.id == arcId }) {
                VStack(alignment: .leading, spacing: 8) {
                    heading(String(format: "%03d. %@", row.n, row.title), subtitle: row.note ?? "")
                    ForEach(row.passages) { ref in
                        VerseChip(label: catalog.refLabel(book: ref.book, chapter: ref.chapter, verse: ref.verse)) {
                            openPassage(ref.book, ref.chapter, ref.verse)
                        }
                    }
                }
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    heading("Arcs \(group)", subtitle: "Tap an arc to open its Scriptures.")
                    ForEach(rows) { row in
                        IndexCard(title: String(format: "%03d. %@", row.n, row.title), subtitle: row.note ?? "") {
                            open(["arcs", group, row.id])
                        }
                    }
                }
            }
        } else {
            VStack(alignment: .leading, spacing: 8) {
                heading("The Arcs of GOD", subtitle: "500 Christ-centered scripture arcs in 10 groups of 50.")
                ForEach(0..<10, id: \.self) { i in
                    let start = i * 50 + 1
                    let end = start + 49
                    let first = data.arcs.first(where: { $0.n == start })
                    let last = data.arcs.first(where: { $0.n == end }) ?? data.arcs.last
                    IndexCard(
                        title: String(format: "Arcs %03d-%03d", start, end),
                        subtitle: "\(first?.title ?? "") to \(last?.title ?? "")"
                    ) {
                        open(["arcs", "\(start)-\(end)"])
                    }
                }
            }
        }
    }
}

private func heading(_ title: String, subtitle: String, color: Color? = nil) -> some View {
    VStack(spacing: 6) {
        Text(title)
            .font(MatrixTheme.titleFont)
            .foregroundStyle(color ?? MatrixTheme.fg)
            .multilineTextAlignment(.center)
        if !subtitle.isEmpty {
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(MatrixTheme.muted)
                .multilineTextAlignment(.center)
        }
    }
    .frame(maxWidth: .infinity)
    .padding(.bottom, 6)
}
