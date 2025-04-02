import SwiftUI
import Foundation
import GoogleSignIn
// import LineSDK // 註解掉

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var showingRegistration = false
    @State private var showingMainView = false
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
                    TextField("學號", text: $email)
                        .textFieldStyle(RoundedTextFieldStyle())
                        .autocapitalization(.none)
                        .keyboardType(.numberPad)
                    
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

                Button(action: handleFacebookLogin) {
                    HStack(spacing: 10) {
                        Image("facebook_logo")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 12, height: 22)
                            .colorInvert()
                        Text("使用 Facebook 登入")
                            .font(.headline)
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color(red: 66/255, green: 103/255, blue: 178/255))
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
                     showingMainView = true // 直接顯示主畫面
                }
                .padding(.top, 20) // 與上方按鈕間隔
                .font(.caption)
                .foregroundColor(.gray)
                
                Spacer()
            }
            .padding(.bottom, 20)
            .navigationBarHidden(true)
        }
        .fullScreenCover(isPresented: $showingMainView) {
            MainTabView()
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
        guard !email.isEmpty else {
            alertMessage = "請輸入學號"
            showingAlert = true
            return
        }
        
        guard !password.isEmpty else {
            alertMessage = "請輸入密碼"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        // TODO: 實作登入邏輯
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isLoading = false
            showingMainView = true
        }
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
        
        let urlString = "http://127.0.0.1:8000/api/social-login/"
        let potentialUrl: URL? = URL(string: urlString)
        
        guard let url = potentialUrl else {
            print("無效的後端 API URL: \(urlString)")
            alertMessage = "內部錯誤：API URL 配置錯誤"
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
        
        guard let requestBody = try? JSONEncoder().encode(body) else {
            print("無法編碼請求主體")
            alertMessage = "內部錯誤：無法準備請求"
            showingAlert = true
            isLoading = false
            return
        }
        request.httpBody = requestBody
        
        print("Sending request to backend: \(url) with body: \(String(data: requestBody, encoding: .utf8) ?? "")")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("後端驗證錯誤: \(error.localizedDescription)")
                    alertMessage = "登入失敗：無法連接伺服器 (\(error.localizedDescription))"
                    showingAlert = true
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("無效的後端回應")
                    alertMessage = "登入失敗：伺服器回應無效"
                    showingAlert = true
                    return
                }
                
                print("Backend response status code: \(httpResponse.statusCode)")
                if let responseData = data {
                    print("Backend response data: \(String(data: responseData, encoding: .utf8) ?? "")")
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    print("後端驗證失敗，狀態碼: \(httpResponse.statusCode)")
                    var backendErrorMsg = "伺服器錯誤"
                    if let data = data, 
                       let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
                       let detail = json["detail"] as? String {
                        backendErrorMsg = detail
                    } else if let data = data, let plainMsg = String(data: data, encoding: .utf8) {
                        backendErrorMsg = plainMsg
                    }
                    alertMessage = "登入失敗：\(backendErrorMsg) (代碼: \(httpResponse.statusCode))"
                    showingAlert = true
                    return
                }
                
                if let data = data {
                    do {
                        if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: String] {
                            let accessToken = json["access"]
                            let refreshToken = json["refresh"]
                            print("後端驗證成功！")
                            print("Access Token: \(accessToken ?? "N/A")")
                            print("Refresh Token: \(refreshToken ?? "N/A")")
                        } else {
                            print("無法解析後端回傳的 Token JSON")
                        }
                    } catch {
                        print("解碼後端回應錯誤: \(error)")
                    }
                }
                showingMainView = true
            }
        }.resume()
    }

    private func handleFacebookLogin() {
        print("Facebook 登入按鈕被點擊 (功能待實作)")
        alertMessage = "Facebook 登入功能開發中"
        showingAlert = true
    }
}

struct RoundedTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(15)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color(.systemGray6))
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
            
            TimetableView() // 課表
                .tabItem {
                    Label("課表", systemImage: "calendar")
                }
            
            TaskView() // 待辦
                .tabItem {
                    Label("待辦", systemImage: "checklist") // 使用 checklist 圖示
                }
                
            MarketplaceView() // 二手市集
                 .tabItem {
                     Label("二手市集", systemImage: "storefront") // 使用 storefront 圖示
                 }

            // 將社群相關視圖包在 NavigationView 中，以便 ChatListView 的導航標題能正常顯示
            NavigationView { 
                 CommunityView() // 社群討論列表
                 // 考慮將聊天列表放在社群 Tab 的第二層或作為獨立 Tab
                 // ChatListView() 
            }
            .tabItem {
                 Label("社群", systemImage: "message.fill") // 使用 message 圖示
            }
            
            // 移除 FriendsView
            /*
            FriendsView()
                .tabItem {
                    Label("好友", systemImage: "message.fill")
                }
            */
        }
    }
}

#Preview {
    LoginView()
} 