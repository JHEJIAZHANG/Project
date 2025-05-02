import Foundation

struct Task: Identifiable {
    let id = UUID()
    var title: String
    var description: String?
    var category: TaskCategory
    var estimatedDuration: TimeInterval // 預計時長（分鐘）
    var isCompleted: Bool = false
    var createdAt: Date = Date()
    var completedAt: Date?
}

enum TaskCategory: String, CaseIterable {
    case study = "學習"
    case work = "工作"
    case exercise = "運動"
    case reading = "閱讀"
    case other = "其他"
    
    var icon: String {
        switch self {
        case .study: return "book.fill"
        case .work: return "briefcase.fill"
        case .exercise: return "figure.run"
        case .reading: return "text.book.closed.fill"
        case .other: return "square.grid.2x2.fill"
        }
    }
    
    var color: String {
        switch self {
        case .study: return "blue"
        case .work: return "purple"
        case .exercise: return "green"
        case .reading: return "orange"
        case .other: return "gray"
        }
    }
} 