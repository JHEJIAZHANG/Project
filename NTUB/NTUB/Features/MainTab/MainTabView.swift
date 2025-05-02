import SwiftUI

struct MainTabView: View {
    // Note: No need to pass AuthManager here,
    // it will receive it from the environment set in NTUBApp.swift
    var body: some View {
        TabView {
            HomeView() // 首頁
                .tabItem {
                    Label("首頁", systemImage: "house.fill")
                }

            // 將社群移到第二個 Tab
            NavigationView {
                 CommunityView() // 社群討論列表
                 // ChatListView()
            }
            .tabItem {
                 Label("社群", systemImage: "message.fill")
            }

            // 移除課表 Tab
            /*
            TimetableView() // 課表
                .tabItem {
                    Label("課表", systemImage: "calendar")
                }
            */

            TaskView() // 待辦 (現在是第三個)
                .tabItem {
                    Label("待辦", systemImage: "checklist")
                }

            MarketplaceView() // 二手市集 (現在是第四個)
                 .tabItem {
                     Label("二手市集", systemImage: "storefront")
                 }

            SettingsView()
                .tabItem {
                    Label("設定", systemImage: "gearshape.fill")
                }
        }
        // Ensure AuthManager is available to all tabs that need it
        // This might not be strictly necessary if already set higher up in NTUBApp,
        // but doesn't hurt to ensure consistency if tabs might be loaded differently.
        // .environmentObject(AuthManager()) // Let's rely on the one from NTUBApp
    }
}

// Add a preview for MainTabView if needed
struct MainTabView_Previews: PreviewProvider {
    static var previews: some View {
        MainTabView()
            .environmentObject(AuthManager()) // Provide dummy for preview
    }
} 