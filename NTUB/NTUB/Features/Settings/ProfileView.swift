import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authManager: AuthManager // Assuming AuthManager holds user info

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // --- Profile Header ---
                HStack(spacing: 15) {
                    Image(systemName: "person.circle.fill") // Placeholder Image
                        .resizable()
                        .scaledToFit()
                        .frame(width: 80, height: 80)
                        .clipShape(Circle())
                        .foregroundColor(.gray)

                    VStack(alignment: .leading) {
                        Text("\(authManager.currentUser?.username ?? "使用者名稱")")
                            .font(.title2)
                            .fontWeight(.bold)
                        // Optionally, display email if available
                        if let email = authManager.currentUser?.email {
                            Text("Email: \(email)")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                        Text("系級: 資訊工程學系 四年級") // Placeholder Department
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    NavigationLink(destination: EditProfileView()) { // Link to Edit Profile
                         Image(systemName: "pencil.circle.fill")
                             .resizable()
                             .frame(width: 30, height: 30)
                             .foregroundColor(.blue)
                     }

                }
                .padding(.horizontal)

                Divider()

                // --- Quick Links ---
                Section(header: Text("快速連結").font(.headline).padding(.horizontal)) {
                    HStack {
                        QuickLinkButton(title: "我的課表", icon: "calendar", destination: TimetableView()) // Placeholder destination
                        QuickLinkButton(title: "我的任務", icon: "list.bullet.clipboard", destination: TaskView()) // Placeholder destination
                        QuickLinkButton(title: "校務系統", icon: "graduationcap", destination: WebView(url: URL(string: "https://ntub.edu.tw")!)) // Example link
                    }
                    .padding(.horizontal)
                }


                Divider()

                // --- App Activity ---
                 Section(header: Text("我的活動").font(.headline).padding(.horizontal)) {
                     NavigationLink(destination: MyPostsView()) { // Placeholder Destination
                         HStack {
                             Image(systemName: "newspaper")
                             Text("我的貼文")
                             Spacer()
                             Image(systemName: "chevron.right")
                         }
                         .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                     }


                     NavigationLink(destination: MyMarketplaceItemsView()) { // Placeholder Destination
                         HStack {
                             Image(systemName: "storefront") // Changed from cart
                             Text("我的市集物品")
                             Spacer()
                             Image(systemName: "chevron.right")
                         }
                         .padding()
                         .background(Color(.systemGray6))
                         .cornerRadius(8)

                     }

                     NavigationLink(destination: MyBookmarksView()) { // Placeholder Destination
                        HStack {
                            Image(systemName: "bookmark")
                            Text("我的收藏")
                            Spacer()
                            Image(systemName: "chevron.right")
                        }
                        .padding()
                       .background(Color(.systemGray6))
                       .cornerRadius(8)
                    }
                     

                 }
                .padding(.horizontal)


                Spacer() // Push Logout to bottom

                // --- Logout Button ---
                Button(action: {
                    authManager.logout()
                }) {
                    Text("登出")
                        .foregroundColor(.red)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                }
                .padding(.horizontal)
                .padding(.bottom) // Add padding at the very bottom
            }
            .padding(.top) // Add padding at the very top of VStack
        }
    }
}

// --- Helper Views (Placeholders) ---

struct QuickLinkButton<Destination: View>: View {
    let title: String
    let icon: String
    let destination: Destination

    var body: some View {
        NavigationLink(destination: destination) {
            VStack {
                Image(systemName: icon)
                    .font(.title2)
                    .frame(width: 50, height: 50)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(10)
                    .foregroundColor(.blue)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
        }
    }
}


// Placeholder View for Web Content
struct WebView: View {
     let url: URL
     var body: some View {
         // In a real app, you'd use WKWebView here
         Text("載入網頁: \\(url.absoluteString)")
             .navigationTitle("網頁")
     }
}


// Placeholder Destination Views (Replace with actual views later)
struct MyPostsView: View {
    var body: some View { Text("我的貼文列表").navigationTitle("我的貼文") }
}

struct MyMarketplaceItemsView: View {
    var body: some View { Text("我的市集物品列表").navigationTitle("我的市集") }
}

struct MyBookmarksView: View {
    var body: some View { Text("我的收藏列表").navigationTitle("我的收藏") }
}


// --- Preview ---
struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileView()
            .environmentObject(AuthManager()) // Provide a dummy AuthManager for preview
    }
} 
