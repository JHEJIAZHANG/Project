import SwiftUI

struct RegistrationView: View {
    @Environment(\.presentationMode) var presentationMode
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var username = ""
    @State private var studentId = ""
    @State private var department = ""
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    // 系所選項
    private let departments = [
        "資訊管理系",
        "企業管理系",
        "財務金融系",
        "會計資訊系",
        "國際商務系",
        "財政稅務系",
        "應用外語系",
        "資訊科技系"
    ]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("基本資料")) {
                    TextField("學號", text: $studentId)
                        .keyboardType(.numberPad)
                    TextField("姓名", text: $username)
                    Picker("系所", selection: $department) {
                        ForEach(departments, id: \.self) { dept in
                            Text(dept).tag(dept)
                        }
                    }
                }
                
                Section(header: Text("帳號設定")) {
                    TextField("電子郵件", text: $email)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                    SecureField("密碼", text: $password)
                        .textContentType(.newPassword)
                    SecureField("確認密碼", text: $confirmPassword)
                        .textContentType(.newPassword)
                }
                
                Section {
                    Button(action: validateAndRegister) {
                        Text("註冊")
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                    }
                }
            }
            .navigationTitle("註冊帳號")
            .navigationBarItems(trailing: Button("取消") {
                presentationMode.wrappedValue.dismiss()
            })
        }
        .alert(isPresented: $showingAlert) {
            Alert(
                title: Text("提示"),
                message: Text(alertMessage),
                dismissButton: .default(Text("確定"))
            )
        }
    }
    
    private func validateAndRegister() {
        // 驗證學號
        guard !studentId.isEmpty else {
            alertMessage = "請輸入學號"
            showingAlert = true
            return
        }
        
        // 驗證姓名
        guard !username.isEmpty else {
            alertMessage = "請輸入姓名"
            showingAlert = true
            return
        }
        
        // 驗證系所
        guard !department.isEmpty else {
            alertMessage = "請選擇系所"
            showingAlert = true
            return
        }
        
        // 驗證電子郵件
        guard isValidEmail(email) else {
            alertMessage = "請輸入有效的電子郵件地址"
            showingAlert = true
            return
        }
        
        // 驗證密碼
        guard password.count >= 6 else {
            alertMessage = "密碼長度至少需要6個字元"
            showingAlert = true
            return
        }
        
        // 驗證密碼確認
        guard password == confirmPassword else {
            alertMessage = "兩次輸入的密碼不一致"
            showingAlert = true
            return
        }
        
        // TODO: 實作註冊邏輯
        // 這裡可以加入實際的註冊API呼叫
        
        // 暫時顯示註冊成功
        alertMessage = "註冊成功！"
        showingAlert = true
        
        // 關閉註冊視圖
        presentationMode.wrappedValue.dismiss()
    }
    
    // 驗證電子郵件格式
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPred = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        return emailPred.evaluate(with: email)
    }
}

#Preview {
    RegistrationView()
} 