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

    // 註解掉整個 init 方法
    /*
    init() {
        // TODO: 將 "YOUR_LINE_CHANNEL_ID" 替換成您真實的 Channel ID
        guard let channelID = Bundle.main.object(forInfoDictionaryKey: "LineChannelID") as? String, !channelID.isEmpty, channelID != "YOUR_LINE_CHANNEL_ID" else {
            fatalError("請在 Info.plist 中設定有效的 LineChannelID")
        }
        LoginManager.shared.setup(channelID: channelID, universalLinkURL: nil)
        print("LINE SDK Initialized with Channel ID: \(channelID)")
    }
    */

    var body: some Scene {
        WindowGroup {
            // 始終從 LoginView 開始
            LoginView()
                .onOpenURL { url in
                    // 優先處理 Google 回調
                    if GIDSignIn.sharedInstance.handle(url) {
                        print("Handled Google Sign-In URL: \(url)")
                        return
                    }
                    // 註解掉處理 LINE 回調的部分
                    /*
                    if LoginManager.shared.application(.shared, open: url) {
                         print("Handled LINE Login URL: \(url)")
                         return
                    }
                    */
                    // 可以加入其他 URL Scheme 處理
                    print("Could not handle URL: \(url)")
                }
        }
    }
}
