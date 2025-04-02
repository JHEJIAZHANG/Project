import SwiftUI

// MARK: - Data Models for Community
struct CommunityPost: Identifiable {
    let id = UUID()
    let authorName: String
    let authorIsAnonymous: Bool
    let postDate: Date
    let content: String
    let topic: PostTopic
    let imageName: String? // Optional image name/URL
    var likes: Int
    var comments: Int
    var isBookmarked: Bool = false
    var isLiked: Bool = false // Track if current user liked it
}

enum PostTopic: String, CaseIterable, Identifiable {
    case all = "全部"
    case study = "課業討論"
    case life = "校園生活"
    case clubs = "社團活動"
    case food = "美食推薦"
    // case market = "二手交易" // Can be added if needed
    var id: String { self.rawValue }

    var color: Color {
        switch self {
        case .all: return .gray
        case .study: return .blue // Match prototype colors
        case .life: return .green
        case .clubs: return .purple
        case .food: return .orange
        }
    }
}

// MARK: - Main Community View (Posts List)
struct CommunityView: View {
    @State private var searchText: String = ""
    @State private var selectedTopic: PostTopic = .all
    @State private var showingAddPostSheet = false
    
    // --- Mock Data ---
    @State private var posts: [CommunityPost] = [
        CommunityPost(authorName: "匿名同學", authorIsAnonymous: true, postDate: Date().addingTimeInterval(-3600*2), content: "有人知道資料庫系統的期中考範圍嗎？聽說會考SQL語法，但不確定具體範圍...", topic: .study, imageName: nil, likes: 5, comments: 3),
        CommunityPost(authorName: "王小明", authorIsAnonymous: false, postDate: Date().addingTimeInterval(-3600*4), content: "推薦學校旁新開的咖啡廳！環境很適合讀書，而且學生證可以打八折喔～", topic: .food, imageName: "photo.fill", likes: 12, comments: 8, isLiked: true),
        CommunityPost(authorName: "李同學", authorIsAnonymous: false, postDate: Date().addingTimeInterval(-3600*6), content: "有人要一起報名下週的程式設計工作坊嗎？", topic: .clubs, imageName: nil, likes: 8, comments: 2),
        CommunityPost(authorName: "匿名同學", authorIsAnonymous: true, postDate: Date().addingTimeInterval(-3600*8), content: "請問圖書館的影印機在哪裡？找了好久都沒看到...", topic: .life, imageName: nil, likes: 2, comments: 1, isBookmarked: true)
    ]
    
    // Filtered posts
    var filteredPosts: [CommunityPost] {
        posts.filter { post in
            let topicMatch = (selectedTopic == .all || post.topic == selectedTopic)
            let searchMatch = searchText.isEmpty || post.content.localizedCaseInsensitiveContains(searchText) || post.authorName.localizedCaseInsensitiveContains(searchText)
            return topicMatch && searchMatch
        }
    }

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 1. Search Bar (Similar to Marketplace)
                 HStack {
                     TextField("搜尋話題...", text: $searchText)
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
                 .padding(.bottom, 10)
                 .padding(.top, -8) // 新增：給搜尋框負的 top padding 將其上移

                // 2. Topic Pills (Similar to Marketplace Categories)
                 ScrollView(.horizontal, showsIndicators: false) {
                     HStack(spacing: 10) {
                         ForEach(PostTopic.allCases) { topic in
                             TopicPill(topic: topic, isSelected: selectedTopic == topic) {
                                 selectedTopic = topic
                             }
                         }
                     }
                     .padding(.horizontal)
                     .padding(.bottom, 15)
                 }

                // 3. Posts List
                List { // Use List for swipe actions later if needed
                    ForEach($posts) { $post in // Use binding to allow interaction
                        // Filter based on selected topic and search text
                         if (selectedTopic == .all || post.topic == selectedTopic) &&
                            (searchText.isEmpty || post.content.localizedCaseInsensitiveContains(searchText) || post.authorName.localizedCaseInsensitiveContains(searchText)) {
                            
                            PostCardView(post: $post) // Pass binding
                                .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)) // Adjust padding
                                .listRowSeparator(.hidden) // Hide default separators
                        }
                    }
                }
                .listStyle(PlainListStyle())
                .background(Color(.systemGray6)) // List background
            }
            .navigationTitle("社群討論")
            .navigationBarTitleDisplayMode(.inline)
            .overlay(alignment: .bottomTrailing) { // Add Post Button
                 Button {
                     showingAddPostSheet = true
                 } label: {
                     Image(systemName: "pencil.circle.fill") // Changed icon to pencil
                         .resizable()
                         .frame(width: 50, height: 50)
                         .foregroundColor(.blue)
                         .background(.white)
                         .clipShape(Circle())
                         .shadow(radius: 5)
                         .padding()
                 }
             }
             .sheet(isPresented: $showingAddPostSheet) {
                  // AddPostView(posts: $posts) // Pass binding later
                  Text("Add Post Sheet Placeholder")
             }
        }
    }
}

// MARK: - Helper Views for Community

// Topic Pill Button
struct TopicPill: View {
    let topic: PostTopic
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(topic.rawValue)
                .font(.caption)
                .padding(.horizontal, 15)
                .padding(.vertical, 8)
                .background(isSelected ? topic.color : Color(.systemGray4)) // Use topic color when selected
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

// Post Card View
struct PostCardView: View {
    @Binding var post: CommunityPost // Use Binding

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Header: Author, Time, Topic
            HStack {
                 Image(systemName: post.authorIsAnonymous ? "person.fill.questionmark" : "person.circle.fill")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 40, height: 40)
                    .foregroundColor(.gray)
                VStack(alignment: .leading) {
                     Text(post.authorIsAnonymous ? "匿名同學" : post.authorName)
                        .font(.headline)
                    Text(post.postDate, style: .relative) // Relative time (e.g., 2 hours ago)
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Spacer()
                 Text(post.topic.rawValue)
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(post.topic.color.opacity(0.2))
                    .foregroundColor(post.topic.color)
                    .cornerRadius(10)
            }

            // Content
            Text(post.content)
                .font(.body)
                .lineLimit(5) // Limit lines shown initially

            // Optional Image
            if let imageName = post.imageName {
                 // Image Placeholder
                 ZStack {
                     RoundedRectangle(cornerRadius: 8)
                        .fill(Color(.systemGray5))
                        .aspectRatio(1.5, contentMode: .fit) // Adjust aspect ratio
                     Image(systemName: imageName)
                         .resizable()
                         .scaledToFit()
                         .frame(maxHeight: 150)
                         .foregroundColor(.gray)
                 }
                 .padding(.vertical, 5)
            }

            // Footer: Likes, Comments, Bookmark
            HStack {
                 Button {
                     post.isLiked.toggle()
                     post.likes += post.isLiked ? 1 : -1
                 } label: {
                     Label("\\(post.likes)", systemImage: post.isLiked ? "heart.fill" : "heart")
                         .foregroundColor(post.isLiked ? .red : .gray)
                 }
                 .buttonStyle(BorderlessButtonStyle())
                 
                 Button {
                      // TODO: Show comments view
                 } label: {
                      Label("\\(post.comments)", systemImage: "bubble.left")
                         .foregroundColor(.gray)
                 }
                 .buttonStyle(BorderlessButtonStyle())

                Spacer()

                 Button {
                     post.isBookmarked.toggle()
                 } label: {
                     Image(systemName: post.isBookmarked ? "bookmark.fill" : "bookmark")
                        .foregroundColor(post.isBookmarked ? .blue : .gray)
                 }
                 .buttonStyle(BorderlessButtonStyle())
            }
            .font(.subheadline)
            .padding(.top, 5)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Add Post View
struct AddPostView: View {
    @Binding var posts: [CommunityPost] // Receive binding
    @Environment(\.presentationMode) var presentationMode

    // Form State
    @State private var postContent: String = ""
    @State private var isAnonymous: Bool = false
    @State private var selectedTopic: PostTopic = .study
    // TODO: Add state for image picking
    // @State private var selectedImage: UIImage?

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 0) { // Use VStack instead of Form for custom layout
                
                // 1. Anonymous Toggle
                HStack {
                    Spacer() // Push toggle to the right
                    Button {
                         isAnonymous = false
                    } label: {
                         Text("實名")
                            .font(.subheadline)
                            .padding(.horizontal, 15)
                            .padding(.vertical, 8)
                            .background(!isAnonymous ? Color.blue : Color(.systemGray5))
                            .foregroundColor(!isAnonymous ? .white : .primary)
                            .cornerRadius(20)
                    }
                    Button {
                         isAnonymous = true
                    } label: {
                         Text("匿名")
                            .font(.subheadline)
                            .padding(.horizontal, 15)
                            .padding(.vertical, 8)
                            .background(isAnonymous ? Color.blue : Color(.systemGray5))
                            .foregroundColor(isAnonymous ? .white : .primary)
                            .cornerRadius(20)
                    }
                }
                .padding()

                // 2. Text Editor
                TextEditor(text: $postContent)
                    .frame(height: 150) // Set initial height
                    .border(Color(.systemGray5), width: 1) // Add a subtle border
                    .padding(.horizontal)
                    .overlay(alignment: .topLeading) { // Placeholder text
                        if postContent.isEmpty {
                            Text("分享你的想法...")
                                .foregroundColor(.gray)
                                .padding(.top, 8)
                                .padding(.leading, 5)
                                .allowsHitTesting(false) // Let taps pass through
                        }
                    }
                    

                // 3. Add Photo Button
                Button {
                    // TODO: Show image picker
                    print("Add photo tapped")
                } label: {
                    HStack {
                        Image(systemName: "camera")
                        Text("添加照片")
                    }
                    .foregroundColor(.blue)
                    .padding()
                }
                
                Divider().padding(.horizontal)

                // 4. Topic Picker
                HStack {
                     Text("選擇話題")
                        .foregroundColor(.gray)
                    Spacer()
                     Picker("選擇話題", selection: $selectedTopic) {
                         ForEach(PostTopic.allCases.filter { $0 != .all }) { topic in // Exclude 'All'
                             Text(topic.rawValue).tag(topic)
                         }
                     }
                     .pickerStyle(.menu) // Use menu style for dropdown
                     .tint(.blue)
                }
                .padding()
                
                Spacer() // Push content to top
            }
            .navigationTitle("發布貼文")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("取消") { presentationMode.wrappedValue.dismiss() },
                trailing: Button("發布") { addPost() }.disabled(postContent.isEmpty) // Disable if no content
            )
        }
    }

    // Function to add the post
    private func addPost() {
        let newPost = CommunityPost(
            authorName: isAnonymous ? "匿名" : "目前使用者", // TODO: Get actual user name
            authorIsAnonymous: isAnonymous,
            postDate: Date(),
            content: postContent,
            topic: selectedTopic,
            imageName: nil, // TODO: Use selected image
            likes: 0,
            comments: 0
        )
        posts.append(newPost)
        presentationMode.wrappedValue.dismiss()
    }
}

// MARK: - Preview
#Preview {
    // Preview AddPostView with a State binding
    StatefulPreviewWrapper(value: []) { binding in
        AddPostView(posts: binding)
    }
    // CommunityView() // Or preview the whole flow
} 