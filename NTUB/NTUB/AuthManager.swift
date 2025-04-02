import SwiftUI
import Combine

class AuthManager: ObservableObject {
    // @Published 屬性包裝器會在值改變時自動通知 SwiftUI 更新視圖
    @Published var isLoggedIn: Bool = false

    // 為了演示方便，暫時使用 UserDefaults 儲存令牌
    // 在正式產品中，應使用 Keychain 來安全地儲存敏感資料
    private var accessTokenKey = "accessToken"
    private var refreshTokenKey = "refreshToken"

    init() {
        // App 啟動時檢查 UserDefaults 中是否已儲存令牌
        if UserDefaults.standard.string(forKey: accessTokenKey) != nil {
             isLoggedIn = true
             print("AuthManager: 發現已儲存的令牌，用戶已登入。")
        } else {
             print("AuthManager: 未發現令牌，用戶未登入。")
             isLoggedIn = false
        }
    }

    // 接收後端返回的令牌並登入
    func login(accessToken: String, refreshToken: String) {
        print("AuthManager: 儲存令牌並設定 isLoggedIn = true")
        UserDefaults.standard.set(accessToken, forKey: accessTokenKey)
        UserDefaults.standard.set(refreshToken, forKey: refreshTokenKey)
        
        // 確保在主線程更新 @Published 屬性
        DispatchQueue.main.async {
            self.isLoggedIn = true
        }
    }
    
    // 用於開發者模式或不需要令牌的登入
    func login() {
        print("AuthManager: 設定 isLoggedIn = true (開發者模式/跳過登入)")
        // 確保在主線程更新 @Published 屬性
         DispatchQueue.main.async {
            self.isLoggedIn = true
        }
    }

    // 登出：清除令牌並更新狀態
    func logout() {
        print("AuthManager: 清除令牌並設定 isLoggedIn = false")
        UserDefaults.standard.removeObject(forKey: accessTokenKey)
        UserDefaults.standard.removeObject(forKey: refreshTokenKey)
        
        // 確保在主線程更新 @Published 屬性
        DispatchQueue.main.async {
            self.isLoggedIn = false
        }
    }
    
    // (可選) 提供方法獲取儲存的 Access Token，供 API 調用時使用
    func getAccessToken() -> String? {
        return UserDefaults.standard.string(forKey: accessTokenKey)
    }
} 