import Foundation

struct StudyPartner: Identifiable {
    let id = UUID()
    var username: String
    var profileImageURL: URL?
    var isOnline: Bool
} 