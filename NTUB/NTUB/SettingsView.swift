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
                    NavigationLink("服務條款", destination: TermsView())
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

// MARK: - Placeholder Destination Views
// Create simple placeholders for NavigationLinks
struct ChangePasswordView: View { var body: some View { Text("更改密碼頁面").navigationTitle("更改密碼") } }
struct LinkedAccountsView: View { var body: some View { Text("綁定的帳號頁面").navigationTitle("綁定的帳號") } }
struct TimetableColorSettingsView: View { var body: some View { Text("課表顏色設定頁面").navigationTitle("課表顏色") } }
struct CommunityPrivacySettingsView: View { var body: some View { Text("社群隱私設定頁面").navigationTitle("社群隱私") } }
struct AboutView: View { var body: some View { Text("關於 App 頁面 (版本號等)").navigationTitle("關於 App") } }
struct FAQView: View { var body: some View { Text("常見問題頁面").navigationTitle("常見問題") } }
struct FeedbackView: View { var body: some View { Text("意見回饋 / 回報問題頁面").navigationTitle("意見回饋") } }
struct TermsView: View { var body: some View { Text("服務條款頁面").navigationTitle("服務條款") } }

// Replace the old PrivacyPolicyView with the detailed version
struct PrivacyPolicyView: View {
    var body: some View {
        ScrollView { // 使用 ScrollView 以容納較長內容
            VStack(alignment: .leading, spacing: 15) {
                Text("隱私權政策")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding(.bottom, 10)

                Text("最後更新日期：[請填寫日期]")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.bottom, 20)

                Text("歡迎使用 NTUB 校園生活 App（以下簡稱「本應用程式」）。我們非常重視您的隱私權，並致力於保護您的個人資訊。本隱私權政策旨在說明我們如何收集、使用、保護及分享您的資訊。請在使用本應用程式前仔細閱讀本政策。")
                    .padding(.bottom, 10)

                SectionView(title: "我們收集的資訊") {
                    Text("為了提供和改進服務，我們可能會收集以下類型的資訊：")
                    Text("• **您提供的資訊：** 例如您在註冊帳號時提供的學號、電子郵件地址、密碼（加密儲存）、您在個人資料中填寫的資訊、您發布的內容（貼文、二手商品資訊等）、您與我們的聯繫資訊。")
                    Text("• **自動收集的資訊：** 例如您的裝置資訊（型號、作業系統版本）、IP 位址、使用日誌、應用程式當機報告、位置資訊（若您授權）、以及您與應用程式互動的數據。")
                    Text("• **[其他可能收集的資訊，例如從第三方服務取得的資訊，若有請補充]**")
                }

                SectionView(title: "我們如何使用您的資訊") {
                    Text("我們將收集到的資訊用於以下目的：")
                    Text("• 提供、維護及改進本應用程式的功能與服務。")
                    Text("• 驗證您的身份並處理您的帳號。")
                    Text("• 回應您的查詢、請求與意見回饋。")
                    Text("• 向您發送重要通知、更新及行銷資訊（若您同意）。")
                    Text("• 進行數據分析與研究，以提升使用者體驗。")
                    Text("• 偵測、預防及處理詐欺、濫用、安全風險或技術問題。")
                    Text("• 遵守相關法律法規要求。")
                    Text("• **[其他特定用途，請補充]**")
                }

                SectionView(title: "資訊分享與揭露") {
                    Text("我們承諾不會將您的個人資訊出售給第三方。我們僅在以下情況下分享您的資訊：")
                    Text("• **徵得您的同意：** 在分享前會取得您的明確同意。")
                    Text("• **服務供應商：** 我們可能會與協助我們營運的第三方服務供應商（例如雲端儲存、數據分析服務）分享必要的資訊，但他們必須遵守本政策或同等的保密義務。")
                    Text("• **法律要求：** 若基於法律、法規、法律程序或政府強制性要求，我們可能必須揭露您的資訊。")
                    Text("• **保護權利：** 為保護本應用程式、我們的使用者或公眾的權利、財產或安全所合理必需的情況下。")
                    Text("• **[其他分享情況，例如匿名化或匯總後的數據，請補充]**")
                }

                SectionView(title: "資訊安全") {
                    Text("我們採取合理的技術和管理措施來保護您的個人資訊，防止未經授權的存取、使用或揭露。然而，網路傳輸或電子儲存方式無法保證 100% 安全，因此我們無法保證資訊的絕對安全。")
                }

                SectionView(title: "您的權利") {
                    Text("根據相關法律，您可能擁有以下權利：")
                    Text("• 存取您的個人資訊。")
                    Text("• 更正不準確的資訊。")
                    Text("• 刪除您的個人資訊（在特定條件下）。")
                    Text("• 限制或反對資訊處理。")
                    Text("• 資料可攜權。")
                    Text("您可以透過 [請提供聯繫方式，例如 App 內設定或客服信箱] 行使您的權利。")
                }

                SectionView(title: "第三方連結與服務") {
                    Text("本應用程式可能包含指向第三方網站或服務的連結。本隱私權政策不適用於這些第三方，建議您查閱其各自的隱私政策。")
                }

                SectionView(title: "兒童隱私") {
                    Text("本應用程式並非為特定年齡以下的兒童設計。我們不會故意收集兒童的個人資訊。**[請根據目標使用者和法規確認具體年齡限制]**")
                }

                SectionView(title: "政策變更") {
                    Text("我們可能會不定時更新本隱私權政策。若有重大變更，我們將透過應用程式內通知或其他適當方式告知您。建議您定期查看本政策以了解最新資訊。")
                }

                SectionView(title: "聯繫我們") {
                    Text("若您對本隱私權政策有任何疑問或疑慮，請透過以下方式聯繫我們：")
                    Text("[請填寫您的聯繫電子郵件或其他聯繫方式]")
                }

                // 強調這是範本
                 Text("---")
                     .padding(.vertical)
                 Text("重要提示：以上為隱私權政策範本內容，僅供參考。請務必諮詢法律專業人士，根據您 App 的實際運作情況、目標地區法規（如 GDPR、CCPA 等）以及收集和使用的具體數據，來撰寫和審閱最終的隱私權政策。")
                     .font(.footnote)
                     .foregroundColor(.red)

            }
            .padding() // 在 VStack 周圍增加內邊距
        }
        .navigationTitle("隱私政策") // 維持導覽標題
    }
}

// Helper View for Sections (Optional, but improves readability)
struct SectionView<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
            content
        }
        .padding(.bottom, 15)
    }
}

struct AccountSecurityView: View {
    var body: some View {
        Text("帳號安全設定頁面") // Placeholder content
            .navigationTitle("帳號安全")
    }
}

// MARK: - Preview
#Preview {
    SettingsView()
        .environmentObject(AuthManager()) // 在預覽中注入一個 AuthManager 實例
} 
