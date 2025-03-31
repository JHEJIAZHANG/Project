import Foundation

struct User: Identifiable {
    let id = UUID()
    var username: String
    var email: String?
    var profileImageURL: URL?
} 