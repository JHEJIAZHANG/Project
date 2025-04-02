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
                Text("註冊")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(agreeToTerms ? Color.blue : Color.gray)
                    .cornerRadius(10)
            }
            .disabled(!agreeToTerms)
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
        
        guard !username.isEmpty else {
            alertMessage = "請輸入姓名"
            showingAlert = true
            return
        }
        
        guard isValidEmail(email) else {
            alertMessage = "請輸入有效的電子郵件地址"
            showingAlert = true
            return
        }
        
        guard password.count >= 6 else {
            alertMessage = "密碼長度至少需要6個字元"
            showingAlert = true
            return
        }
        
        guard password == confirmPassword else {
            alertMessage = "兩次輸入的密碼不一致"
            showingAlert = true
            return
        }
        
        guard agreeToTerms else {
            alertMessage = "請先閱讀並同意服務條款和隱私政策"
            showingAlert = true
            return
        }
        
        alertMessage = "註冊成功！"
        showingAlert = true
        
        presentationMode.wrappedValue.dismiss()
    }
    
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPred = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        return emailPred.evaluate(with: email)
    }
}

#Preview {
    RegistrationView()
} 