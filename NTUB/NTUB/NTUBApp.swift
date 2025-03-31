//
//  NTUBApp.swift
//  NTUB
//
//  Created by Aibox on 2025/3/31.
//

import SwiftUI

@main
struct NTUBApp: App {
    // 使用 @State 來管理登入狀態
    @State private var isLoggedIn = false // 預設為未登入

    var body: some Scene {
        WindowGroup {
            // 根據登入狀態決定顯示哪個 View
            if isLoggedIn {
                ContentView() // 已登入，顯示主內容
            } else {
                LoginView() // 未登入，顯示登入頁面，不再需要傳遞 isLoggedIn
            }
        }
    }
}
