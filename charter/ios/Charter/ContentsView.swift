import SwiftUI

struct ContentsView: View {
    let doc: CharterDocument
    let activeBiteId: String
    let onSelect: (String) -> Void

    private var groups: [(String, [Bite])] {
        var result: [(String, [Bite])] = []
        for bite in doc.bites {
            if result.last?.0 == bite.group {
                result[result.count - 1].1.append(bite)
            } else {
                result.append((bite.group, [bite]))
            }
        }
        return result
    }

    var body: some View {
        NavigationStack {
            List {
                ForEach(groups, id: \.0) { group, bites in
                    Section(group) {
                        ForEach(bites) { bite in
                            Button {
                                onSelect(bite.id)
                            } label: {
                                HStack {
                                    Text(bite.cite)
                                        .foregroundStyle(.primary)
                                    Spacer()
                                    if bite.id == activeBiteId {
                                        Image(systemName: "text.quote")
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Contents")
            .navigationBarTitleDisplayMode(.inline)
        }
        .presentationDetents([.medium, .large])
    }
}
