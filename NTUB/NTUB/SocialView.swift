import SwiftUI

struct SocialView: View {
    @State private var selectedTab = 0
    @State private var searchText = ""
    @State private var showingNewPost = false
    @State private var showingNewItem = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 分段控制器
                Picker("內容類型", selection: $selectedTab) {
                    Text("社群討論").tag(0)
                    Text("二手交易").tag(1)
                    Text("聊天室").tag(2)
                }
                .pickerStyle(.segmented)
                .padding()
                
                // 搜尋欄
                SearchBar(text: $searchText)
                    .padding(.horizontal)
                
                // 內容區域
                TabView(selection: $selectedTab) {
                    // 社群討論版面
                    CommunityView(showingNewPost: $showingNewPost)
                        .tag(0)
                    
                    // 二手交易版面
                    MarketplaceView(showingNewItem: $showingNewItem)
                        .tag(1)
                    
                    // 聊天室列表
                    ChatRoomListView()
                        .tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
            .navigationTitle(navigationTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        if selectedTab == 0 {
                            showingNewPost = true
                        } else if selectedTab == 1 {
                            showingNewItem = true
                        }
                    }) {
                        Image(systemName: "plus")
                    }
                }
            }
        }
    }
    
    var navigationTitle: String {
        switch selectedTab {
        case 0: return "社群討論"
        case 1: return "二手交易"
        case 2: return "聊天室"
        default: return ""
        }
    }
}

// 社群討論視圖
struct CommunityView: View {
    @Binding var showingNewPost: Bool
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(0..<10) { _ in
                    PostCard()
                }
            }
            .padding()
        }
        .sheet(isPresented: $showingNewPost) {
            NavigationView {
                Text("新增貼文")
                    .navigationTitle("發布貼文")
                    .navigationBarItems(trailing: Button("發布") {
                        showingNewPost = false
                    })
            }
        }
    }
}

// 貼文卡片
struct PostCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 作者資訊
            HStack {
                Image(systemName: "person.circle.fill")
                    .resizable()
                    .frame(width: 40, height: 40)
                    .foregroundColor(.gray)
                VStack(alignment: .leading) {
                    Text("匿名用戶")
                        .font(.headline)
                    Text("2小時前")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Spacer()
                Text("課程討論")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.1))
                    .foregroundColor(.blue)
                    .cornerRadius(8)
            }
            
            // 貼文內容
            Text("有人修過統計學嗎？想請教一下作業的問題...")
                .font(.body)
            
            // 互動按鈕
            HStack {
                Button(action: {}) {
                    Label("讚 (12)", systemImage: "hand.thumbsup")
                }
                Spacer()
                Button(action: {}) {
                    Label("留言 (5)", systemImage: "message")
                }
                Spacer()
                Button(action: {}) {
                    Label("分享", systemImage: "square.and.arrow.up")
                }
            }
            .foregroundColor(.gray)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

// 二手交易視圖
struct MarketplaceView: View {
    @Binding var showingNewItem: Bool
    
    var body: some View {
        ScrollView {
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                ForEach(0..<10) { _ in
                    ItemCard()
                }
            }
            .padding()
        }
        .sheet(isPresented: $showingNewItem) {
            NavigationView {
                Text("刊登商品")
                    .navigationTitle("刊登二手物品")
                    .navigationBarItems(trailing: Button("發布") {
                        showingNewItem = false
                    })
            }
        }
    }
}

// 商品卡片
struct ItemCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // 商品圖片
            Rectangle()
                .fill(Color.gray.opacity(0.2))
                .aspectRatio(1, contentMode: .fit)
                .overlay(
                    Image(systemName: "book.fill")
                        .resizable()
                        .scaledToFit()
                        .padding(30)
                        .foregroundColor(.gray)
                )
            
            // 商品資訊
            VStack(alignment: .leading, spacing: 4) {
                Text("統計學課本")
                    .font(.headline)
                    .lineLimit(2)
                Text("九成新")
                    .font(.caption)
                    .foregroundColor(.gray)
                Text("NT$ 350")
                    .font(.callout)
                    .foregroundColor(.blue)
            }
            .padding(.horizontal, 8)
            .padding(.bottom, 8)
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

// 聊天室列表視圖
struct ChatRoomListView: View {
    var body: some View {
        List {
            ForEach(0..<10) { _ in
                ChatRoomRow()
            }
        }
        .listStyle(PlainListStyle())
    }
}

// 聊天室列表項目
struct ChatRoomRow: View {
    var body: some View {
        HStack {
            Image(systemName: "person.circle.fill")
                .resizable()
                .frame(width: 50, height: 50)
                .foregroundColor(.gray)
            
            VStack(alignment: .leading, spacing: 4) {
                Text("王小明")
                    .font(.headline)
                Text("請問書還在嗎？")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("14:30")
                    .font(.caption)
                    .foregroundColor(.gray)
                Circle()
                    .fill(Color.blue)
                    .frame(width: 20, height: 20)
                    .overlay(
                        Text("2")
                            .font(.caption2)
                            .foregroundColor(.white)
                    )
            }
        }
        .padding(.vertical, 8)
    }
}

// 搜尋欄元件
struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
            
            TextField("搜尋用戶", text: $text)
                .textFieldStyle(PlainTextFieldStyle())
            
            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

#Preview {
    SocialView()
} 