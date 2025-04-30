//
//  NTUBApp.swift
//  NTUB
//
//  Created by Aibox on 2025/3/31.
//

import SwiftUI // 確保 import SwiftUI 存在
// import LineSDK // 註解掉
import GoogleSignIn

@main
struct NTUBApp: App {
    // 使用 @StateObject 創建並管理 AuthManager 實例
    @StateObject private var authManager = AuthManager()

    // MARK: - App Lifecycle

    var body: some Scene {
        WindowGroup {
            // 根據登入狀態決定顯示哪個 View
            if authManager.isLoggedIn {
                MainTabView()
                    .environmentObject(authManager) // 將 AuthManager 注入環境
            } else {
                LoginView()
                    .environmentObject(authManager) // 將 AuthManager 注入環境
            }
        }
    }

    // MARK: - Google Sign-In Callback
    // ... existing code ...
    
    // MARK: - LINE Sign-In Callback
    // ... existing code ...
}

// Helper Extension for App Delegate Setup
// ... existing code ...
