import SwiftUI

// Helper View for Sections (Optional, but improves readability)
// 如果 SectionView 在多個地方使用，可以考慮移到 Core/Views
struct SectionView<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
            content
        }
        .padding(.bottom, 15)
    }
} 