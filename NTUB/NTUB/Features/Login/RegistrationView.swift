import SwiftUI

struct RegistrationView: View {
    @Environment(\.presentationMode) var presentationMode
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var username = ""
    @State private var studentId = ""
    @State private var agreeToTerms = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack {
                Button {
                    presentationMode.wrappedValue.dismiss()
                } label: {
                    Image(systemName: "arrow.left")
                        .font(.title2)
                        .foregroundColor(.primary)
                }
                Spacer()
            }
            .padding(.bottom, 10)

            Text("註冊")
                .font(.largeTitle)
                .fontWeight(.bold)
                .padding(.bottom, 10)

            VStack(alignment: .leading, spacing: 15) {
                Text("基本資料").font(.headline).padding(.bottom, 5)
                TextField("姓名", text: $username)
                    .textFieldStyle(RoundedTextFieldStyle())
                    TextField("學號", text: $studentId)
                        .keyboardType(.numberPad)
                    .textFieldStyle(RoundedTextFieldStyle())
            }
            
            VStack(alignment: .leading, spacing: 15) {
                Text("帳號設定").font(.headline).padding(.bottom, 5).padding(.top)
                TextField("信箱", text: $email)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                    .textFieldStyle(RoundedTextFieldStyle())
                    SecureField("密碼", text: $password)
                        .textContentType(.newPassword)
                    .textFieldStyle(RoundedTextFieldStyle())
                    SecureField("確認密碼", text: $confirmPassword)
                        .textContentType(.newPassword)
                    .textFieldStyle(RoundedTextFieldStyle())
            }
            
            HStack {
                Image(systemName: agreeToTerms ? "checkmark.square.fill" : "square")
                    .foregroundColor(agreeToTerms ? .blue : .gray)
                    .onTapGesture {
                        agreeToTerms.toggle()
                    }
                Text("我同意")
                    .font(.footnote)
                Link("服務條款", destination: URL(string: "https://example.com/terms")!)
                    .font(.footnote)
                    .foregroundColor(.blue)
                Text("和")
                    .font(.footnote)
                Link("隱私政策", destination: URL(string: "https://example.com/privacy")!)
                    .font(.footnote)
                    .foregroundColor(.blue)
                Spacer()
            }
            .padding(.top, 10)
            
            Spacer()

                    Button(action: validateAndRegister) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.gray)
                        .cornerRadius(10)
                } else {
                    Text("註冊")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(agreeToTerms ? Color.blue : Color.gray)
                        .cornerRadius(10)
                }
            }
            .disabled(!agreeToTerms || isLoading)
            .padding(.bottom)
        }
        .padding(.horizontal, 30)
        .padding(.top)
        .alert(isPresented: $showingAlert) {
            Alert(
                title: Text("提示"),
                message: Text(alertMessage),
                dismissButton: .default(Text("確定"))
            )
        }
    }
    
    private func validateAndRegister() {
        guard !studentId.isEmpty else {
            alertMessage = "請輸入學號"
            showingAlert = true
            return
        }
        
        guard isValidEmail(email) else {
            alertMessage = "請輸入有效的電子郵件地址"
            showingAlert = true
            return
        }
        
        guard agreeToTerms else {
            alertMessage = "請先閱讀並同意服務條款和隱私政策"
            showingAlert = true
            return
        }
        
        isLoading = true
        
        let urlString = "http://127.0.0.1:8000/api/register/"
        guard let url = URL(string: urlString) else {
            print("無效的後端註冊 API URL: \\(urlString)")
            alertMessage = "內部錯誤：API URL 配置錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: String] = [
            "username": studentId,
            "email": email,
            "password": password
        ]
        
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            print("無法編碼註冊請求主體: \\(error)")
            alertMessage = "註冊請求格式錯誤"
            showingAlert = true
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("註冊請求錯誤: \\(error.localizedDescription)")
                    alertMessage = "註冊失敗，請檢查網路連線或稍後再試。\\(error.localizedDescription)"
            showingAlert = true
            return
        }
        
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("無效的註冊回應")
                    alertMessage = "註冊失敗：收到無效的回應。"
                    showingAlert = true
                    return
                }

                guard let data = data else {
                    print("註冊回應沒有收到資料")
                    alertMessage = "註冊失敗：未收到伺服器資料。"
        showingAlert = true
                    return
                }

                print("註冊回應狀態碼: \\(httpResponse.statusCode)")
                print("註冊回應資料: \\(String(data: data, encoding: .utf8) ?? \"無法解碼\")")
        
                if httpResponse.statusCode == 201 {
                    alertMessage = "註冊成功！請使用您的學號和密碼登入。"
                    showingAlert = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
        presentationMode.wrappedValue.dismiss()
    }
                } else {
                    do {
                        let errorResponse = try JSONDecoder().decode(RegistrationErrorResponse.self, from: data)
                        var errorMessage = "註冊失敗："
                        if let usernameErrors = errorResponse.username {
                            errorMessage += "\\n帳號(學號): \(usernameErrors.joined(separator: ", "))"
                        }
                        if let emailErrors = errorResponse.email {
                            errorMessage += "\\n信箱: \(emailErrors.joined(separator: ", "))"
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
                        print("無法解碼註冊錯誤回應: \\(error)")
                        alertMessage = "註冊失敗，狀態碼：\\(httpResponse.statusCode)。請檢查輸入或伺服器錯誤。"
                        showingAlert = true
                    }
                }
            }
        }.resume()
    }
    
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPred = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        return emailPred.evaluate(with: email)
    }
}

struct RegistrationErrorResponse: Codable {
    let username: [String]?
    let email: [String]?
    let password: [String]?
    let non_field_errors: [String]?
}

#Preview {
    RegistrationView()
} 