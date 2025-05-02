import Foundation // Added for UUID
import SwiftUI

// MARK: - Data Models for Timetable
struct ScheduleCourse: Identifiable {
    let id = UUID()
    var name: String
    var location: String
    var day: Weekday // 星期幾
    var startTime: Int // 開始小時 (24小時制, e.g., 8, 10, 13)
    var endTime: Int   // 結束小時 (e.g., 10, 12, 15) - 不含結束時間點
    var color: Color
    // Consider adding:
    // var teacher: String?
    // var notes: String?
}

enum Weekday: Int, CaseIterable, Identifiable {
    case monday = 1, tuesday, wednesday, thursday, friday //, saturday, sunday
    var id: Int { self.rawValue }

    var shortName: String {
        switch self {
        case .monday: return "一"
        case .tuesday: return "二"
        case .wednesday: return "三"
        case .thursday: return "四"
        case .friday: return "五"
        // case .saturday: return "六"
        // case .sunday: return "日"
        }
    }
} 