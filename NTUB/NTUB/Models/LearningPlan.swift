import Foundation

struct LearningPlan: Identifiable {
    let id = UUID()
    var title: String
    var description: String?
    var deadline: Date?
    var isCompleted: Bool = false
    var associatedCourse: String?
} 