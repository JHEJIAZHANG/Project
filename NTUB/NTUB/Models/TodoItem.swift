import SwiftUI

// MARK: - TodoItem Model
struct TodoItem: Identifiable, Hashable { // Conforming to Hashable for ForEach grouping
    let id = UUID()
    var title: String
    var category: TodoCategory = .study // 新增分類
    var dueDate: Date?
    var priority: Priority = .medium
    var reminder: ReminderOption = .none // 新增提醒選項
    var notes: String? // 新增備註
    var isCompleted: Bool = false

    enum Priority: String, CaseIterable, Identifiable {
        case high = "重要", medium = "中等", low = "一般"
        var id: String { self.rawValue }
        
        var color: Color {
            switch self {
            case .high: return .red
            case .medium: return .orange
            case .low: return .blue // 調整顏色以匹配原型
            }
        }
    }
    
    enum TodoCategory: String, CaseIterable, Identifiable {
        case study = "課業", life = "生活"
        var id: String { self.rawValue }
    }
    
    enum ReminderOption: String, CaseIterable {
        case none = "不提醒"
        case min15 = "提前15分鐘"
        case min30 = "提前30分鐘"
        case hour1 = "提前1小時"
        case day1 = "提前1天"
    }
    
    // Helper to get deadline string like in HomeView
    var deadlineString: String {
        guard let date = dueDate else { return "無截止日期" }
        let formatter = DateFormatter()
        if Calendar.current.isDateInToday(date) {
            formatter.dateFormat = "HH:mm 截止"
            return formatter.string(from: date)
        } else {
            formatter.dateFormat = "MM/dd"
            return formatter.string(from: date)
        }
    }
} 