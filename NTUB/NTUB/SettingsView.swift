import SwiftUI

struct SettingsView: View {
    // 從環境獲取 AuthManager
    @EnvironmentObject var authManager: AuthManager
    
    // --- State Variables for Toggles ---
    // Account & Security
    // @State private var useAppLock = false // 移除
    
    // Notifications
    @State private var masterNotifications = true
    @State private var classReminders = true
    @State private var todoReminders = true
    @State private var marketplaceNotifications = true
    @State private var communityNotifications = true
    @State private var announcementNotifications = true

    // Appearance
    // @AppStorage("darkModeEnabled") private var darkModeEnabled = false // 移除
    // 使用 AppStorage 直接存儲選擇的主題原始值 (String)
    @AppStorage("selectedTheme") private var selectedThemeRawValue: String = ThemeOption.system.rawValue

    enum ThemeOption: String, CaseIterable, Identifiable {
        case system = "跟隨系統", light = "淺色", dark = "深色"
        var id: String { self.rawValue }
    }
    
    // --- Body ---
    var body: some View {
        NavigationView {
            List { // Use List instead of Form for more control over style
                
                // MARK: - 帳號與安全
                Section("帳號與安全") {
                    NavigationLink(destination: ProfileView()) { // Link to Profile Edit View
                         HStack {
                             Image(systemName: "person.crop.circle")
                                 .foregroundColor(.gray)
                                 .imageScale(.large)
                             Text("個人資料管理")
                         }
                    }
                    NavigationLink("更改密碼", destination: ChangePasswordView())
                    NavigationLink("綁定的帳號", destination: LinkedAccountsView())
                    // Toggle("啟用應用程式鎖定 (Face ID/Touch ID)", isOn: $useAppLock) // 移除
                }

                // MARK: - 通知設定
                Section("通知設定") {
                     Toggle("所有通知", isOn: $masterNotifications)
                    // Allow granular control only if master is enabled
                    Group {
                        Toggle("課程提醒", isOn: $classReminders)
                        Toggle("待辦事項提醒", isOn: $todoReminders)
                        Toggle("二手市集通知", isOn: $marketplaceNotifications)
                        Toggle("社群通知", isOn: $communityNotifications)
                        Toggle("學校公告", isOn: $announcementNotifications)
                    }
                    .disabled(!masterNotifications)
                    .foregroundColor(masterNotifications ? .primary : .gray)
                }
                
                // MARK: - 外觀與顯示
                Section("外觀與顯示") {
                     // 綁定到 AppStorage 的 RawValue
                     Picker("佈景主題", selection: $selectedThemeRawValue) {
                         ForEach(ThemeOption.allCases) { option in
                             Text(option.rawValue).tag(option.rawValue) // tag 使用 rawValue
                         }
                     }
                     // NavigationLink("課表顏色", destination: TimetableColorSettingsView())
                     // TODO: Add Text Size adjustment if needed
                }
                .onChange(of: selectedThemeRawValue) { newThemeRawValue in
                     // Apply theme change (implementation depends on how you handle themes)
                     print("Theme changed to: \(newThemeRawValue)")
                     // 從 RawValue 轉換回 Enum
                     if let newTheme = ThemeOption(rawValue: newThemeRawValue) {
                          applyTheme(newTheme)
                     }
                 }

                // MARK: - 隱私設定
                Section("隱私設定") {
                     NavigationLink("課表共享管理", destination: ShareScheduleView()) // Reuse existing view
                     // NavigationLink("社群隱私", destination: CommunityPrivacySettingsView())
                }
                
                // MARK: - 關於與支援
                Section("關於與支援") {
                    NavigationLink("關於 App", destination: AboutView())
                    NavigationLink("常見問題 (FAQ)", destination: FAQView())
                    NavigationLink("意見回饋 / 回報問題", destination: FeedbackView())
                    NavigationLink("服務條款", destination: TermsView())
                    NavigationLink("隱私政策", destination: PrivacyPolicyView())
                }
                
                // MARK: - 登出
                Section {
                     Button("登出") {
                         // TODO: Implement logout logic
                         print("Logout button tapped")
                         // Example: Clear tokens, navigate to LoginView
                         authManager.logout() // 調用 AuthManager 的登出方法
                     }
                     .foregroundColor(.red)
                     .frame(maxWidth: .infinity, alignment: .center)
                }
            }
            .listStyle(InsetGroupedListStyle()) // Use inset grouped style
            .navigationTitle("設定")
            // 在視圖出現時應用儲存的主題設定
            .onAppear {
                 if let initialTheme = ThemeOption(rawValue: selectedThemeRawValue) {
                     applyTheme(initialTheme)
                 }
            }
        }
    }
    
    // 修改 applyTheme 以真正改變 App 外觀
    private func applyTheme(_ theme: ThemeOption) {
        print("Applying theme: \(theme.rawValue)")
        
        // 獲取所有連接的 Scene
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return }
        
        // 遍歷 Scene 中的所有 Window 並設置 overrideUserInterfaceStyle
        windowScene.windows.forEach { window in
            switch theme {
            case .light:
                window.overrideUserInterfaceStyle = .light
            case .dark:
                window.overrideUserInterfaceStyle = .dark
            case .system:
                window.overrideUserInterfaceStyle = .unspecified // 跟隨系統
            }
        }
    }
}

// MARK: - Placeholder Destination Views
// Create simple placeholders for NavigationLinks
struct ProfileView: View { var body: some View { Text("個人資料管理頁面").navigationTitle("個人資料") } }
struct ChangePasswordView: View { var body: some View { Text("更改密碼頁面").navigationTitle("更改密碼") } }
struct LinkedAccountsView: View { var body: some View { Text("綁定的帳號頁面").navigationTitle("綁定的帳號") } }
struct TimetableColorSettingsView: View { var body: some View { Text("課表顏色設定頁面").navigationTitle("課表顏色") } }
struct CommunityPrivacySettingsView: View { var body: some View { Text("社群隱私設定頁面").navigationTitle("社群隱私") } }
struct AboutView: View { var body: some View { Text("關於 App 頁面 (版本號等)").navigationTitle("關於 App") } }
struct FAQView: View { var body: some View { Text("常見問題頁面").navigationTitle("常見問題") } }
struct FeedbackView: View { var body: some View { Text("意見回饋 / 回報問題頁面").navigationTitle("意見回饋") } }
struct TermsView: View { var body: some View { Text("服務條款頁面").navigationTitle("服務條款") } }
struct PrivacyPolicyView: View { var body: some View { Text("隱私政策頁面").navigationTitle("隱私政策") } }


// MARK: - Preview
#Preview {
    SettingsView()
        .environmentObject(AuthManager()) // 在預覽中注入一個 AuthManager 實例
} 