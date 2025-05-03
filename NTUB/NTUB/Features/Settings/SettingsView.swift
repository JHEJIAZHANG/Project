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
                    NavigationLink("服務條款", destination: TermsView()) // Added TermsView link
                    NavigationLink("隱私政策", destination: PrivacyPolicyView())
                }

                // MARK: - 進階設定 (新增)
                Section { // 可以放在獨立 Section 或合併到"關於與支援"下方
                    NavigationLink("進階設定", destination: AccountSecurityView())
                }

                // MARK: - 登出

            } // End of List
            .listStyle(InsetGroupedListStyle()) // Use inset grouped style
            .navigationTitle("設定")
            // 在視圖出現時應用儲存的主題設定
            .onAppear {
                 if let initialTheme = ThemeOption(rawValue: selectedThemeRawValue) {
                     applyTheme(initialTheme)
                 }
            }
        } // <-- 在此處加上缺失的大括號
    } // End of body
    
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

// Placeholder Destination Views - REMOVE ALL BELOW THIS LINE UNTIL MARK: - Preview

// MARK: - Preview
#Preview {
    SettingsView()
        .environmentObject(AuthManager()) // 在預覽中注入一個 AuthManager 實例
} 
