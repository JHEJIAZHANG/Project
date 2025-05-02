import Foundation
import SwiftUI

struct CalendarEvent: Identifiable {
    let id = UUID()
    var title: String
    var startDate: Date
    var endDate: Date
    var color: Color = .blue
    var description: String?
} 