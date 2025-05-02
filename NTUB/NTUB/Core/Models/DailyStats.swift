import Foundation

struct DailyStats {
    var date: Date
    var totalStudyTime: TimeInterval
    var studySessions: Int
}

// Helper to format TimeInterval
extension TimeInterval {
    func formattedDuration() -> String {
        let formatter = DateComponentsFormatter()
        formatter.allowedUnits = [.hour, .minute]
        formatter.unitsStyle = .abbreviated
        return formatter.string(from: self) ?? "0m"
    }
} 