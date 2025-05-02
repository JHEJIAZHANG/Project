import Foundation

// MARK: - Date Extension for Start of Week
extension Date {
    /// 計算包含該日期的週的星期一 (根據 ISO 8601 標準，一週從星期一開始)
    var startOfWeek: Date? {
        let calendar = Calendar(identifier: .iso8601) // 使用 ISO 8601 日曆
        guard let _ = calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: self).yearForWeekOfYear else { return nil } // 確保能獲取年份
        return calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: self))
    }
} 