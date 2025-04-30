import SwiftUI
import Combine

class AuthManager: ObservableObject {
    // @Published 屬性包裝器會在值改變時自動通知 SwiftUI 更新視圖
    @Published var isLoggedIn: Bool = false
    @Published var currentUser: User? = nil // 新增：儲存當前用戶資訊

    // 為了演示方便，暫時使用 UserDefaults 儲存令牌
    // 在正式產品中，應使用 Keychain 來安全地儲存敏感資料
    private var accessTokenKey = "accessToken"
    private var refreshTokenKey = "refreshToken"

    init() {
        // App 啟動時檢查 UserDefaults 中是否已儲存令牌
        if let token = UserDefaults.standard.string(forKey: accessTokenKey) {
             isLoggedIn = true
             print("AuthManager: 發現已儲存的令牌，用戶已登入。嘗試獲取用戶資料...")
             // 如果已登入，嘗試立即獲取用戶資料
             fetchUserProfile(accessToken: token)
        } else {
             print("AuthManager: 未發現令牌，用戶未登入。")
             isLoggedIn = false
             currentUser = nil // 確保未登入時 currentUser 為 nil
        }
    }

    // 接收後端返回的令牌並登入
    func login(accessToken: String, refreshToken: String) {
        print("AuthManager: 儲存令牌並設定 isLoggedIn = true")
        UserDefaults.standard.set(accessToken, forKey: accessTokenKey)
        UserDefaults.standard.set(refreshToken, forKey: refreshTokenKey)
        
        // 登入成功後，獲取用戶資料
        fetchUserProfile(accessToken: accessToken)

        // 確保在主線程更新 @Published 屬性
        DispatchQueue.main.async {
            self.isLoggedIn = true
        }
    }
    
    // 用於開發者模式或不需要令牌的登入
    func login() {
        print("AuthManager: 設定 isLoggedIn = true (開發者模式/跳過登入)")
        // 開發者模式可能需要設置假資料或保持 nil
        DispatchQueue.main.async {
            self.isLoggedIn = true
            // self.currentUser = User(id: 0, username: "Developer", email: "dev@example.com", studentId: "DEV001") // 可選：設置假資料
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
            self.currentUser = nil // 登出時清除用戶資料
        }
    }
    
    // (可選) 提供方法獲取儲存的 Access Token，供 API 調用時使用
    func getAccessToken() -> String? {
        return UserDefaults.standard.string(forKey: accessTokenKey)
    }

    // 新增：從後端獲取用戶資料的方法 (佔位符)
    private func fetchUserProfile(accessToken: String) {
        print("AuthManager: 正在獲取用戶資料...")
        // TODO: 實作 API 呼叫
        // 1. 準備 URL (例如 http://127.0.0.1:8000/api/user/profile/)
        // 2. 建立 URLRequest，設置 HTTP Method 為 GET
        // 3. 在 Header 中加入 Authorization: Bearer <accessToken>
        // 4. 發送請求 (URLSession.shared.dataTask)
        // 5. 處理回應：
        //    - 成功 (HTTP 200): 解碼 JSON 回應為 User 物件
        //    - 失敗 (例如 401 Unauthorized): 可能需要刷新 token 或處理錯誤
        // 6. 在主線程更新 self.currentUser

        // --- 佔位符：模擬延遲和成功 --- 
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { // 模擬網路延遲
            // 假設成功獲取並解碼了 User 資料
            let fetchedUser = User(username: "FetchedUser", email: "user@ntub.edu.tw", profileImageURL: nil) // Removed id, email is optional, removed studentId
            print("AuthManager: 成功獲取用戶資料: \(fetchedUser)")
            self.currentUser = fetchedUser
        }
        // --- 佔位符結束 ---
    }
} 