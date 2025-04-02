import SwiftUI

// MARK: - Data Models for Chat
struct Chat: Identifiable {
    let id = UUID()
    let participantName: String // Or Group Name
    let lastMessage: String
    let lastMessageDate: Date
    let avatarName: String // System name for icon or image name
    let unreadCount: Int
    let isGroupChat: Bool
}

// MARK: - Main Chat List View
struct ChatListView: View {
    @State private var searchText: String = ""
    
    // --- Mock Data ---
    @State private var chats: [Chat] = [
        Chat(participantName: "王小明", lastMessage: "好的，那我們圖書館見", lastMessageDate: Date().addingTimeInterval(-300), avatarName: "person.circle.fill", unreadCount: 2, isGroupChat: false),
        Chat(participantName: "資料庫小組", lastMessage: "林小華：報告進度更新了嗎？", lastMessageDate: Date().addingTimeInterval(-86400 + 1800), avatarName: "person.3.fill", unreadCount: 0, isGroupChat: true),
        Chat(participantName: "陳老師", lastMessage: "收到，謝謝你。", lastMessageDate: Date().addingTimeInterval(-86400 * 2), avatarName: "person.crop.circle.badge.checkmark", unreadCount: 0, isGroupChat: false),
        Chat(participantName: "班級群組", lastMessage: "下週班會時間地點不變", lastMessageDate: Date().addingTimeInterval(-86400 * 3), avatarName: "person.2.gobackward", unreadCount: 5, isGroupChat: true)
    ]
    
    // Filtered chats
    var filteredChats: [Chat] {
        chats.filter {
            searchText.isEmpty || $0.participantName.localizedCaseInsensitiveContains(searchText) || $0.lastMessage.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 1. Search Bar
                HStack {
                     TextField("搜尋聊天...", text: $searchText)
                         .padding(10)
                         .padding(.leading, 30)
                         .background(Color(.systemGray6))
                         .cornerRadius(10)
                         .overlay(
                             HStack {
                                 Image(systemName: "magnifyingglass")
                                     .foregroundColor(.gray)
                                     .padding(.leading, 8)
                                 Spacer()
                             }
                         )
                 }
                 .padding(.horizontal)
                 .padding(.bottom, 10) // Less vertical padding than posts list
                
                // 2. Chat List
                List {
                    ForEach(filteredChats) { chat in
                         NavigationLink(destination: ChatRoomView(chat: chat)) {
                             ChatRowView(chat: chat)
                        }
                    }
                }
                .listStyle(PlainListStyle())
            }
            .navigationTitle("聊天")
            // Use default large title display mode
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        // TODO: Implement new chat/edit logic
                        print("Edit/New Chat button tapped")
                    } label: {
                         Image(systemName: "square.and.pencil")
                    }
                }
            }
        }
    }
}

// MARK: - Chat Row View
struct ChatRowView: View {
    let chat: Chat
    
    var body: some View {
        HStack(spacing: 15) {
            Image(systemName: chat.avatarName) // Use avatarName for system icon
                .resizable()
                .scaledToFit()
                .frame(width: 50, height: 50)
                .foregroundColor(.gray)
                .clipShape(Circle()) // Make avatar circular
                .overlay(Circle().stroke(Color(.systemGray5), lineWidth: 1))
                
            VStack(alignment: .leading, spacing: 4) {
                Text(chat.participantName)
                    .font(.headline)
                Text(chat.lastMessage)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .lineLimit(1)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                 Text(chat.lastMessageDate, style: .time) // Show time or relative date
                    .font(.caption)
                    .foregroundColor(.gray)
                if chat.unreadCount > 0 {
                    Text("\\(chat.unreadCount)")
                        .font(.caption)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.red)
                        .foregroundColor(.white)
                        .clipShape(Capsule())
                }
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Chat Room View (Placeholder)
struct ChatRoomView: View {
    let chat: Chat
    
    var body: some View {
        Text("聊天室 with \\(chat.participantName)")
            .navigationTitle(chat.participantName)
            .navigationBarTitleDisplayMode(.inline)
            // TODO: Implement chat message bubbles, input field, etc.
    }
}

// MARK: - Preview
#Preview {
    ChatListView()
} 