import Foundation

struct StudyStats {
    var date: Date
    var focusTime: TimeInterval
    var completedTasks: Int
    var category: TaskCategory
    
    static func mockWeeklyData() -> [StudyStats] {
        let calendar = Calendar.current
        return (0...6).map { daysAgo in
            let date = calendar.date(byAdding: .day, value: -daysAgo, to: Date()) ?? Date()
            return StudyStats(
                date: date,
                focusTime: TimeInterval.random(in: 1800...7200),  // 30分鐘到2小時
                completedTasks: Int.random(in: 2...8),
                category: TaskCategory.allCases.randomElement() ?? .study
            )
        }.reversed()
    }
    
    static func mockCategoryData() -> [StudyStats] {
        return TaskCategory.allCases.map { category in
            StudyStats(
                date: Date(),
                focusTime: TimeInterval.random(in: 3600...14400),  // 1小時到4小時
                completedTasks: Int.random(in: 5...15),
                category: category
            )
        }
    }
} 