import Foundation

// MARK: - Chat Data Models
struct Chat: Identifiable {
    let id = UUID()
    var partnerName: String
    var partnerAvatar: String? // Placeholder
    var lastMessage: String
    var lastMessageTimestamp: Date
    var unreadCount: Int
}

struct ChatMessage: Identifiable {
    let id = UUID()
    var text: String
    var isSentByUser: Bool
    var timestamp: Date
} 