import SwiftUI

// MARK: - Chat Data Models
// Removed Chat and ChatMessage definitions from here

// MARK: - Main Chat View (List)
struct ChatView: View {
    @State private var searchText: String = ""
    
    // --- Mock Data (Updated to match Chat model) ---
    @State private var chats: [Chat] = [
        Chat(partnerName: "王小明", partnerAvatar: "person.circle.fill", lastMessage: "好的，那我們圖書館見", lastMessageTimestamp: Date().addingTimeInterval(-300), unreadCount: 2),
        Chat(partnerName: "資料庫小組", partnerAvatar: "person.3.fill", lastMessage: "林小華：報告進度更新了嗎？", lastMessageTimestamp: Date().addingTimeInterval(-86400 + 1800), unreadCount: 0),
        Chat(partnerName: "陳老師", partnerAvatar: "person.crop.circle.badge.checkmark", lastMessage: "收到，謝謝你。", lastMessageTimestamp: Date().addingTimeInterval(-86400 * 2), unreadCount: 0),
        Chat(partnerName: "班級群組", partnerAvatar: "person.2.gobackward", lastMessage: "下週班會時間地點不變", lastMessageTimestamp: Date().addingTimeInterval(-86400 * 3), unreadCount: 5)
    ]
    
    // Filtered chats
    var filteredChats: [Chat] {
        chats.filter {
            // Updated filter logic to use partnerName
            searchText.isEmpty || $0.partnerName.localizedCaseInsensitiveContains(searchText) || $0.lastMessage.localizedCaseInsensitiveContains(searchText)
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
            Image(systemName: chat.partnerAvatar ?? "person.circle") // Use partnerAvatar
                .resizable()
                .scaledToFit()
                .frame(width: 50, height: 50)
                .foregroundColor(.gray)
                .clipShape(Circle()) // Make avatar circular
                .overlay(Circle().stroke(Color(.systemGray5), lineWidth: 1))
                
            VStack(alignment: .leading, spacing: 4) {
                Text(chat.partnerName) // Use partnerName
                    .font(.headline)
                Text(chat.lastMessage)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .lineLimit(1)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                 Text(chat.lastMessageTimestamp, style: .time) // Use lastMessageTimestamp
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
        Text("聊天室 with \(chat.partnerName)") // Use partnerName
            .navigationTitle(chat.partnerName) // Use partnerName
            .navigationBarTitleDisplayMode(.inline)
            // TODO: Implement chat message bubbles, input field, etc.
    }
}

// MARK: - Preview
#Preview {
    ChatView()
} 