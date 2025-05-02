import Foundation
import SwiftUI // Added for Color

// MARK: - Community Data Model
struct CommunityPost: Identifiable {
    let id = UUID()
    var authorName: String
    var authorAvatar: String? // Placeholder for avatar image name/URL
    var timestamp: Date = Date()
    var content: String
    var images: [String]? // Placeholder for image names/URLs
    var likes: Int = 0
    var comments: Int = 0
    var topic: PostTopic? // Changed back to PostTopic?, Optional topic/tag
    var isLiked: Bool = false // Track if the current user liked this post
}

// Added PostTopic Enum definition here
enum PostTopic: String, CaseIterable, Identifiable {
    case all = "全部"
    case study = "課業討論"
    case life = "校園生活"
    case clubs = "社團活動"
    case food = "美食推薦"
    // case market = "二手交易" // Can be added if needed
    var id: String { self.rawValue }

    // Add color if needed elsewhere, or handle in View
    var color: Color {
        switch self {
        case .all: return .gray
        case .study: return .blue
        case .life: return .green
        case .clubs: return .purple
        case .food: return .orange
        }
    }
} 