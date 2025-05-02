import Foundation
import SwiftUI // For Color

// MARK: - Marketplace Data Model
struct MarketplaceItem: Identifiable {
    let id = UUID()
    var title: String
    var description: String
    var price: Double
    var sellerName: String
    var sellerContact: String? // Optional contact info
    var category: ItemCategory // Changed back to ItemCategory
    var condition: String // e.g., "全新", "九成新"
    var imageName: String? // Placeholder for image name/URL
    var postDate: Date = Date()
    var isSold: Bool = false
    // Add color for category tag if needed
    // var categoryColor: Color = .blue
}

// Added ItemCategory Enum definition here
enum ItemCategory: String, CaseIterable, Identifiable {
    case all = "全部"
    case textbook = "教科書"
    case stationery = "文具用品"
    case electronics = "3C產品"
    case lifestyle = "生活用品" // Added lifestyle category
    case others = "其他物品"
    var id: String { self.rawValue }
} 