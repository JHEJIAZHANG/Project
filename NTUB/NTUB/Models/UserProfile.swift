import Foundation

struct UserProfile: Identifiable {
    let id = UUID()
    var username: String
    var profileImageURL: URL?
    var level: Int
    var totalStudyTime: TimeInterval
    var completedTasks: Int
    var isOnline: Bool
    var rank: Int?
    
    static func mockProfiles() -> [UserProfile] {
        return [
            UserProfile(username: "Alice", level: 15, totalStudyTime: 150 * 3600, completedTasks: 120, isOnline: true, rank: 1),
            UserProfile(username: "Bob", level: 12, totalStudyTime: 120 * 3600, completedTasks: 95, isOnline: false, rank: 2),
            UserProfile(username: "Charlie", level: 10, totalStudyTime: 100 * 3600, completedTasks: 80, isOnline: true, rank: 3),
            UserProfile(username: "David", level: 8, totalStudyTime: 80 * 3600, completedTasks: 65, isOnline: false, rank: 4),
            UserProfile(username: "Eva", level: 7, totalStudyTime: 70 * 3600, completedTasks: 55, isOnline: true, rank: 5)
        ]
    }
} 