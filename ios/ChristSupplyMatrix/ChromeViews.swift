import SwiftUI

struct MatrixChromeModifier: ViewModifier {
    let showBack: Bool
    @Binding var navigationPath: [Destination]

    func body(content: Content) -> some View {
        content
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(MatrixTheme.bg.opacity(0.92), for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbarColorScheme(.dark, for: .navigationBar)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    VStack(spacing: 1) {
                        Text(Brand.site)
                            .font(MatrixTheme.kickerFont)
                            .foregroundStyle(MatrixTheme.gold)
                            .tracking(1.6)
                            .textCase(.uppercase)
                        Text(Brand.name)
                            .font(.system(size: 11, weight: .semibold, design: .monospaced))
                            .foregroundStyle(MatrixTheme.fg)
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                }
                if showBack {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Contents") {
                            navigationPath.removeAll()
                        }
                        .font(MatrixTheme.kickerFont)
                        .foregroundStyle(MatrixTheme.gold)
                    }
                }
            }
            .background(MatrixBackground())
    }
}

extension View {
    func matrixChrome(showBack: Bool, navigationPath: Binding<[Destination]>) -> some View {
        modifier(MatrixChromeModifier(showBack: showBack, navigationPath: navigationPath))
    }
}

struct EqualMark: View {
    var body: some View {
        (Text("All Users Are Created Equally By ")
            .foregroundStyle(MatrixTheme.fg)
         + Text("God")
            .foregroundStyle(MatrixTheme.accent)
            .fontWeight(.semibold))
            .font(MatrixTheme.kickerFont)
            .tracking(1.1)
            .textCase(.uppercase)
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity)
            .padding(.bottom, 8)
            .accessibilityLabel(Brand.equal)
    }
}

struct LiberateMark: View {
    var body: some View {
        Text(Brand.liberate)
            .font(MatrixTheme.kickerFont)
            .tracking(1.1)
            .foregroundStyle(MatrixTheme.fg)
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity)
            .padding(.top, 14)
    }
}

struct CreditMark: View {
    var body: some View {
        VStack(spacing: 6) {
            Text(Brand.credit)
                .font(.system(size: 11, weight: .medium, design: .default))
                .foregroundStyle(MatrixTheme.muted)
                .multilineTextAlignment(.center)
            Link(Brand.site, destination: Brand.siteURL)
                .font(MatrixTheme.kickerFont)
                .foregroundStyle(MatrixTheme.gold)
        }
        .frame(maxWidth: .infinity)
        .padding(.bottom, 8)
    }
}

struct IndexCard: View {
    let title: String
    var subtitle: String = ""
    var color: Color? = nil
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(MatrixTheme.headlineFont)
                    .foregroundStyle(color ?? MatrixTheme.fg)
                    .multilineTextAlignment(.leading)
                    .tracking(0.4)
                if !subtitle.isEmpty {
                    Text(subtitle)
                        .font(.subheadline)
                        .foregroundStyle(MatrixTheme.muted)
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, 14)
            .padding(.vertical, 13)
            .frame(minHeight: 52)
            .background(MatrixTheme.bg.opacity(0.7))
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(MatrixTheme.line, lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
    }
}

struct VerseChip: View {
    let label: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(label)
                .font(.body.weight(.medium))
                .foregroundStyle(MatrixTheme.fg)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 14)
                .padding(.vertical, 12)
                .frame(minHeight: 48)
                .background(MatrixTheme.bg.opacity(0.7))
                .overlay(
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(MatrixTheme.line, lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }
}

struct LetterChip: View {
    let title: String
    var count: Int? = nil
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Text(title)
                    .font(.body.weight(.semibold))
                    .foregroundStyle(MatrixTheme.fg)
                if let count {
                    Text("\(count)")
                        .font(MatrixTheme.monoFont)
                        .foregroundStyle(MatrixTheme.gold)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .frame(minHeight: 44)
            .background(MatrixTheme.bg.opacity(0.7))
            .overlay(
                Capsule()
                    .stroke(MatrixTheme.line, lineWidth: 1)
            )
            .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}

struct Kicker: View {
    let text: String
    var body: some View {
        Text(text)
            .font(MatrixTheme.kickerFont)
            .tracking(2)
            .foregroundStyle(MatrixTheme.muted)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.top, 10)
            .padding(.bottom, 2)
    }
}

struct IndexSheet<Content: View>: View {
    @ViewBuilder var content: () -> Content

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 8) {
                EqualMark()
                content()
                LiberateMark()
                CreditMark()
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
            .padding(.bottom, 28)
        }
        .scrollIndicators(.hidden)
    }
}
