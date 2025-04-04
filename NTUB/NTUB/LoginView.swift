import SwiftUI
import Foundation
import GoogleSignIn
import LineSDK // 取消註解 LineSDK
// import LineSDK // 註解掉

struct LoginView: View {
    // 從環境獲取 AuthManager
    @EnvironmentObject var authManager: AuthManager
    
    @State private var identifier = "" // 改為 identifier 以符合後端
    @State private var password = ""
    @State private var showingRegistration = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var isLoading = false
    
    // 新增 ViewModel 實例 (如果需要管理登入後的狀態或與後端互動)
    // @StateObject private var viewModel = LoginViewModel() // 暫時註解，如果需要複雜狀態管理再開啟

    var body: some View {
        NavigationView {
            VStack(spacing: 15) {
                Text("登入")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 30)
                    .padding(.bottom, 30)

                VStack(spacing: 15) {
                    TextField("學號或電子郵件", text: $identifier)
                        .textFieldStyle(RoundedTextFieldStyle())
                        .autocapitalization(.none)
                    
                    SecureField("密碼", text: $password)
                        .textFieldStyle(RoundedTextFieldStyle())
                }
                .padding(.horizontal, 30)

                HStack {
                    Spacer()
                    Button("忘記密碼？") {
                        print("忘記密碼按鈕被點擊")
                    }
                    .font(.footnote)
                    .foregroundColor(.blue)
                }
                .padding(.horizontal, 30)
                .padding(.top, 5)
                .padding(.bottom, 20)

                Button(action: handleLogin) {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("登入")
                            .font(.headline)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
                .padding(.top, 10)
                .disabled(isLoading)

                HStack {
                    VStack { Divider().background(Color.gray.opacity(0.5)) }
                    Text("或")
                        .font(.caption)
                        .foregroundColor(.gray)
                    VStack { Divider().background(Color.gray.opacity(0.5)) }
                }
                .padding(.horizontal, 30)
                .padding(.vertical, 20)

                Button(action: handleGoogleSignIn) {
                    HStack(spacing: 10) {
                        Image("google_logo")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 20, height: 20)
                        Text("使用 Google 登入")
                            .font(.headline)
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.white)
                .foregroundColor(.gray)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                )
                .padding(.horizontal, 30)
                .disabled(isLoading)

                Button(action: handleLineLogin) {
                    HStack(spacing: 10) {
                        Image("line_logo")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 24, height: 24)
                        Text("使用 LINE 登入")
                            .font(.headline)
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color(red: 0/255, green: 185/255, blue: 0/255))
                .cornerRadius(10)
                .padding(.horizontal, 30)
                .padding(.top, 10)
                .disabled(isLoading)

                Button(action: { showingRegistration = true }) {
                    Text("還沒有帳號？立即註冊")
                        .foregroundColor(.blue)
                }
                .padding(.top, 30)

                Button("開發者模式：跳過登入") {
                    print("開發者模式按鈕觸發：跳過登入")
                    authManager.login() // 調用 AuthManager 的無參數登入方法
                }
                .padding(.top, 20) // 與上方按鈕間隔
                .font(.caption)
                .foregroundColor(.gray)
                
                Spacer()
            }
            .padding(.bottom, 20)
            .navigationBarHidden(true)
        }
        .sheet(isPresented: $showingRegistration) {
            RegistrationView()
        }
        .alert("提示", isPresented: $showingAlert) {
            Button("確定", role: .cancel) { }
        } message: {
            Text(alertMessage)
        }
    }
    
    private func handleLogin() {
        // 驗證 identifier 和 password 是否為空
        guard !identifier.isEmpty else {
            alertMessage = "請輸入學號或電子郵件"
            showingAlert = true
            return
        }
        
        guard !password.isEmpty else {
            alertMessage = "請輸入密碼"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        // 後端登入 API URL
        let urlString = "http://127.0.0.1:8000/api/login/"
        guard let url = URL(string: urlString) else {
            print("無效的後端 API URL: \\(urlString)")
            alertMessage = "內部錯誤：API URL 配置錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: String] = [
            "identifier": identifier,
            "password": password
        ]
        
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            print("無法編碼請求主體: \\(error)")
            alertMessage = "請求格式錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("登入請求錯誤: \\(error.localizedDescription)")
                    alertMessage = "登入失敗，請檢查網路連線或稍後再試。\\(error.localizedDescription)"
                    showingAlert = true
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("無效的回應")
                    alertMessage = "登入失敗：收到無效的回應。"
                    showingAlert = true
                    return
                }

                guard let data = data else {
                    print("沒有收到資料")
                    alertMessage = "登入失敗：未收到伺服器資料。"
                    showingAlert = true
                    return
                }

                print("狀態碼: \\(httpResponse.statusCode)")
                print("回應資料: \\(String(data: data, encoding: .utf8) ?? \"無法解碼\")")


                if httpResponse.statusCode == 200 {
                    // 登入成功
                    do {
                        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
                        print("登入成功！")
                        print("Access Token: \\(loginResponse.access)")
                        print("Refresh Token: \\(loginResponse.refresh)")
                        
                        // TODO: 將 token 安全地儲存 (例如 Keychain)
                        // UserDefaults.standard.set(loginResponse.access, forKey: "accessToken")
                        // UserDefaults.standard.set(loginResponse.refresh, forKey: "refreshToken")
                        
                        authManager.login(accessToken: loginResponse.access, refreshToken: loginResponse.refresh)
                    } catch {
                        print("無法解碼登入回應: \\(error)")
                        alertMessage = "登入失敗：無法處理伺服器回應。\\(error)"
                        showingAlert = true
                    }
                } else {
                    // 登入失敗，嘗試解析錯誤訊息
                    do {
                        let errorResponse = try JSONDecoder().decode(LoginErrorResponse.self, from: data)
                         // 組合錯誤訊息
                        var errorMessage = "登入失敗："
                        if let detail = errorResponse.detail {
                            errorMessage += "\\n\(detail)"
                        }
                        if let identifierErrors = errorResponse.identifier {
                            errorMessage += "\\n帳號/信箱: \(identifierErrors.joined(separator: ", "))"
                        }
                        if let passwordErrors = errorResponse.password {
                            errorMessage += "\\n密碼: \(passwordErrors.joined(separator: ", "))"
                        }
                        if let nonFieldErrors = errorResponse.non_field_errors {
                             errorMessage += "\\n\(nonFieldErrors.joined(separator: ", "))"
                        }
                         alertMessage = errorMessage
                         showingAlert = true
                    } catch {
                        // 如果無法解析特定錯誤結構，顯示通用錯誤
                        print("無法解碼錯誤回應: \\(error)")
                        alertMessage = "登入失敗，狀態碼：\(httpResponse.statusCode)。請檢查輸入或稍後再試。"
                        showingAlert = true
                    }
                }
            }
        }.resume() // 啟動請求
    }
    
    private func handleGoogleSignIn() {
        isLoading = true
        
        guard let clientID = Bundle.main.object(forInfoDictionaryKey: "GoogleClientID") as? String else {
            print("Error: Google Client ID not found in Info.plist")
            alertMessage = "Google 登入設定錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        let config = GIDConfiguration(clientID: clientID)
        GIDSignIn.sharedInstance.configuration = config
        
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first(where: { $0.isKeyWindow }),
              let rootViewController = window.rootViewController else {
            print("Error: Unable to get root view controller.")
            alertMessage = "無法啟動 Google 登入"
            showingAlert = true
            isLoading = false
            return
        }
        
        GIDSignIn.sharedInstance.signIn(withPresenting: rootViewController) { result, error in
            isLoading = false
            
            if let error = error {
                if (error as NSError).code == GIDSignInError.canceled.rawValue {
                    print("Google Sign-In Canceled")
                } else {
                    print("Google Sign-In Error: \(error.localizedDescription)")
                    alertMessage = "Google 登入失敗: \(error.localizedDescription)"
                    showingAlert = true
                }
                return
            }
            
            guard let user = result?.user else {
                print("Google Sign-In Error: Missing user information or result.")
                alertMessage = "無法取得 Google 登入資訊"
                showingAlert = true
                return
            }

            let accessToken = user.accessToken.tokenString

            print("Google Sign-In Successful! Access Token: \(accessToken)")
            verifyTokenWithBackend(provider: "google", accessToken: accessToken)
        }
    }

    private func verifyTokenWithBackend(provider: String, accessToken: String) {
        isLoading = true
        
        // 確保 URL 正確
        let urlString = "http://127.0.0.1:8000/api/social-login/" // 這裡可能是 Google 登入的後端驗證 URL
        guard let url = URL(string: urlString) else {
            print("無效的後端社交登入 API URL: \\(urlString)")
            alertMessage = "內部錯誤：社交登入 API URL 配置錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: String] = [
            "provider": provider,
            "access_token": accessToken
        ]
        
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            print("無法編碼社交登入請求主體: \\(error)")
            alertMessage = "社交登入請求格式錯誤"
            showingAlert = true
            isLoading = false
            return
        }

         URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false // 確保無論成功或失敗都停止加載指示器

                if let error = error {
                    print("社交登入驗證請求錯誤: \\(error.localizedDescription)")
                    alertMessage = "社交登入驗證失敗：\\(error.localizedDescription)"
                    showingAlert = true
                    return
                }

                guard let httpResponse = response as? HTTPURLResponse, let data = data else {
                    print("無效的社交登入驗證回應")
                    alertMessage = "社交登入驗證失敗：收到無效的回應。"
                    showingAlert = true
                    return
                }

                print("社交登入驗證狀態碼: \\(httpResponse.statusCode)")
                print("社交登入驗證回應資料: \\(String(data: data, encoding: .utf8) ?? \"無法解碼\")")


                if httpResponse.statusCode == 200 {
                    // 社交登入驗證成功
                    do {
                        // 假設社交登入成功後也返回類似的 Token 結構
                        let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
                        print("社交登入驗證成功！")
                        print("Access Token: \\(loginResponse.access)")
                        print("Refresh Token: \\(loginResponse.refresh)")

                        // TODO: 將 token 安全地儲存 (例如 Keychain)
                        // UserDefaults.standard.set(loginResponse.access, forKey: "accessToken")
                        // UserDefaults.standard.set(loginResponse.refresh, forKey: "refreshToken")

                        authManager.login(accessToken: loginResponse.access, refreshToken: loginResponse.refresh)
                    } catch {
                        print("無法解碼社交登入驗證回應: \\(error)")
                        alertMessage = "社交登入驗證失敗：無法處理伺服器回應。"
                        showingAlert = true
                    }
                } else {
                    // 社交登入驗證失敗
                     // 嘗試解析可能的錯誤訊息結構 (可以根據後端實際返回調整)
                    var backendErrorMessage = "社交登入驗證失敗。"
                    if let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
                       let detail = json["detail"] as? String {
                        backendErrorMessage += "\\n\(detail)"
                    } else if let responseString = String(data: data, encoding: .utf8) {
                         backendErrorMessage += "\\n伺服器回應：\(responseString)"
                    }
                    
                    alertMessage = backendErrorMessage
                    showingAlert = true
                }
            }
        }.resume()
    }

    // 新增用於解碼登入成功回應的結構
    struct LoginResponse: Codable {
        let access: String
        let refresh: String
    }

    // 新增用於解碼登入失敗回應的結構 (根據後端可能的錯誤格式調整)
    struct LoginErrorResponse: Codable {
        let detail: String?
        let identifier: [String]? // 根據後端 Serializer 的 field name
        let password: [String]?
        let non_field_errors: [String]? // Django REST framework 常見的非欄位錯誤
    }

    // 新增 LINE 登入處理函數 (目前是 placeholder)
    private func handleLineLogin() {
        print("LINE 登入按鈕被點擊")
        isLoading = true
        // TODO: 實作 LINE SDK 登入邏輯
        // 1. 初始化 LineSDK (可能需要在 App Delegate 或 Scene Delegate)
        // 2. 調用 LoginManager.shared.login()
        // 3. 在 App Delegate 或 Scene Delegate 或 .onOpenURL 中處理回調，獲取授權碼
        // 4. 將授權碼發送到後端 /api/social-login/ 進行驗證和 Token 交換

        // 暫時模擬失敗，顯示提示
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
             isLoading = false
             alertMessage = "LINE 登入功能尚未完整實作。"
             showingAlert = true
        }
    }

    // 處理 Facebook 登入的函數 (保留或刪除)
    private func handleFacebookLogin() {
        print("Facebook 登入按鈕被點擊")
        // TODO: 實作 Facebook 登入邏輯
        // 需要整合 Facebook SDK
        alertMessage = "Facebook 登入功能尚未實作。"
        showingAlert = true
    }
}

struct RoundedTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.vertical, 15)
            .padding(.horizontal, 20)
            .background(Color(UIColor.systemGray6)) // 使用 systemGray6 更符合 iOS 風格
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.gray.opacity(0.2), lineWidth: 1) // 細微邊框
            )
    }
}

struct MainTabView: View {
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
            
            SettingsView() // 設定 (現在是第五個)
                .tabItem {
                    Label("設定", systemImage: "gear")
                }
        }
    }
}

#Preview {
    LoginView()
} 