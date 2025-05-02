import SwiftUI

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
// Removed SectionView struct definition from here 