import SwiftUI

struct FriendsView: View {
    var body: some View {
        NavigationView {
            VStack {
                Text("好友頁面")
                    .font(.largeTitle)
                    .padding()
                // TODO: 在這裡加入好友相關的內容和邏輯
                Spacer()
            }
            .navigationTitle("好友")
        }
    }
}

#Preview {
    FriendsView()
} 