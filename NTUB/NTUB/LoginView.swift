import SwiftUI
import GoogleSignIn
// import LineSDK  // 暫時註解

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var showingRegistration = false
    @State private var showingMainView = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Logo 區域
                VStack(spacing: 10) {
                    Image(systemName: "graduationcap.fill")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 80, height: 80)
                        .foregroundColor(.blue)
                    
                    Text("NTUB 校園助手")
                        .font(.title)
                        .fontWeight(.bold)
                }
                .padding(.top, 50)
                
                // 輸入區域
                VStack(spacing: 15) {
                    TextField("電子郵件", text: $email)
                        .textFieldStyle(RoundedTextFieldStyle())
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                    
                    SecureField("密碼", text: $password)
                        .textFieldStyle(RoundedTextFieldStyle())
                }
                .padding(.horizontal, 30)
                .padding(.top, 30)
                
                // 登入按鈕
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
                .padding(.horizontal, 30)
                .padding(.top, 20)
                .disabled(isLoading)

                // 分隔線
                Text("或")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.vertical, 10)

                // Google 登入按鈕
                Button(action: handleGoogleSignIn) {
                    HStack {
                        Image(systemName: "g.circle.fill")
                            .resizable()
                            .frame(width: 20, height: 20)
                        Text("使用 Google 登入")
                            .font(.headline)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.white)
                .foregroundColor(.black)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                )
                .padding(.horizontal, 30)
                .disabled(isLoading)
                
                // 註冊連結
                Button(action: { showingRegistration = true }) {
                    Text("還沒有帳號？立即註冊")
                        .foregroundColor(.blue)
                }
                .padding(.top, 20)
                
                Spacer()
                
                // 版本資訊
                Text("Version 1.0.0")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.bottom, 20)
            }
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
    
    // MARK: - 私有方法
    private func handleLogin() {
        guard !email.isEmpty else {
            alertMessage = "請輸入電子郵件"
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
        
        // TODO: 實作 Google 登入邏輯
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isLoading = false
            showingMainView = true
        }
    }
}

// MARK: - 自定義樣式
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

// MARK: - 主要分頁視圖
struct MainTabView: View {
    var body: some View {
        TabView {
            Text("課表")
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("課表")
                }
            
            Text("社群")
                .tabItem {
                    Image(systemName: "bubble.left.and.bubble.right")
                    Text("社群")
                }
        }
    }
}

#Preview {
    LoginView()
} 