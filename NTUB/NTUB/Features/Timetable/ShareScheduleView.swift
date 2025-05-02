import SwiftUI

// MARK: - Mock Data for Shared Friends
struct SharedFriend: Identifiable {
    let id = UUID()
    let name: String
    let studentId: String // Or some identifier
    // Add profile picture URL if needed
}

// MARK: - Share Schedule View
struct ShareScheduleView: View {
    @Environment(\.presentationMode) var presentationMode
    
    // --- State Variables ---
    @State private var isSharingEnabled = true
    @State private var showDetailedInfo = true
    @State private var shareLink = "https://ntub.app/share/c/123456" // Example link
    
    // Mock data for friends list
    @State private var sharedFriends: [SharedFriend] = [
        SharedFriend(name: "王小明", studentId: "1092XXXXX"),
        SharedFriend(name: "林小華", studentId: "1092XXXXX")
    ]

    var body: some View {
        // --- 暫時註解掉 body 內容以進行診斷 ---
        Text("Testing ShareScheduleView")
            .onTapGesture { presentationMode.wrappedValue.dismiss() }
            .navigationTitle("共享課表 (Test)") // 添加標題以確認視圖加載
        /*
        NavigationView {
            List { // Using List for better structure and scrolling
                
                // Section 1: Sharing Settings
                Section("共享設定") {
                    Toggle("開啟課表共享", isOn: $isSharingEnabled)
                    Toggle("包含課程詳細資訊", isOn: $showDetailedInfo)
                        .disabled(!isSharingEnabled) // Only enable if sharing is on
                        .foregroundColor(isSharingEnabled ? .primary : .gray)
                }
                
                // Section 2: Share Link
                Section("共享連結") {
                    HStack {
                        TextField("共享連結", text: $shareLink)
                            .disabled(true) // Make it read-only
                            .foregroundColor(.gray)
                        Spacer()
                        Button {
                            UIPasteboard.general.string = shareLink
                            // Optional: Show a confirmation message
                        } label: {
                            Image(systemName: "doc.on.doc")
                        }
                    }
                    Button("產生新連結") {
                        // TODO: Implement logic to generate a new link
                        shareLink = "https://ntub.app/share/c/\(UUID().uuidString.prefix(6))" // Generate a dummy new link
                    }
                }
                .disabled(!isSharingEnabled) // Disable link section if sharing is off
                
                // Section 3: Shared Friends List
                Section("已共享的好友") {
                    if sharedFriends.isEmpty {
                        Text("尚未與任何人共享")
                            .foregroundColor(.gray)
                    } else {
                        ForEach(sharedFriends) { friend in
                            HStack {
                                Image(systemName: "person.circle.fill") // Placeholder icon
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 40, height: 40)
                                    .foregroundColor(.gray.opacity(0.5))
                                VStack(alignment: .leading) {
                                    Text(friend.name).font(.headline)
                                    Text(friend.studentId).font(.caption).foregroundColor(.gray)
                                }
                                Spacer()
                                Button {
                                    // TODO: Implement logic to remove friend
                                    removeFriend(friend)
                                } label: {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.gray)
                                }
                                .buttonStyle(BorderlessButtonStyle()) // Prevent row selection on button tap
                            }
                        }
                    }
                    Button("添加好友") {
                        // TODO: Implement logic to show friend picker or search
                        print("添加好友按鈕被點擊")
                    }
                }
                .disabled(!isSharingEnabled) // Disable friends section if sharing is off
                
            }
            .listStyle(InsetGroupedListStyle()) // Use InsetGroupedListStyle for modern look
            .navigationTitle("共享課表")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(leading: Button("完成") { // Changed from Cancel to Done
                presentationMode.wrappedValue.dismiss()
            })
        }
        */
        // --- 註解結束 ---
    }
    
    // Helper function to remove a friend (mock implementation)
    private func removeFriend(_ friendToRemove: SharedFriend) {
        sharedFriends.removeAll { $0.id == friendToRemove.id }
    }
}

// MARK: - Preview
#Preview {
    ShareScheduleView()
} 