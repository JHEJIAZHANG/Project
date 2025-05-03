
import SwiftUI

struct TermsView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 15) {
                Text("服務條款")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.bottom)

                Text("歡迎使用 NTUB 校園生活 App！")
                    .font(.title2)

                Text("在使用本應用程式（以下簡稱「本 App」）前，請仔細閱讀以下服務條款（以下簡稱「本條款」）。當您開始使用本 App，即表示您已閱讀、瞭解並同意接受本條款的所有內容。如果您不同意本條款的任何部分，請勿使用本 App。")
                    .padding(.bottom)

                SectionView(title: "1. 接受條款") {
                    Text("您確認您已達到法定年齡，能夠訂立具約束力的合約，或已取得父母或法定監護人的同意使用本 App。")
                }

                SectionView(title: "2. 服務內容") {
                    Text("本 App 提供校園資訊、課表管理、待辦事項、二手市集、社群互動等相關功能（實際功能以 App 提供為準）。我們保留隨時修改、暫停或終止部分或全部服務的權利，恕不另行通知。")
                }

                SectionView(title: "3. 使用者行為") {
                    Text("您同意不使用本 App 從事任何非法或禁止的活動，包括但不限於：")
                    Text("- 發布不實、誹謗、侮辱、威脅、騷擾、歧視或令人反感的內容。")
                    Text("- 侵害他人智慧財產權或其他權利。")
                    Text("- 散播病毒、惡意軟體或其他可能損害本 App 或其他使用者裝置的程式碼。")
                    Text("- 未經授權存取或試圖存取他人帳戶或系統。")
                    Text("- 從事任何商業廣告活動（二手市集功能除外）。")
                }
                
                SectionView(title: "4. 智慧財產權") {
                    Text("本 App 及其所有內容（包括文字、圖片、圖示、軟體等）的智慧財產權均歸開發者或相關權利人所有。未經事先書面同意，您不得複製、修改、散布、公開傳輸或以其他方式使用。")
                }

                SectionView(title: "5. 隱私權政策") {
                    Text("我們重視您的隱私。關於我們如何收集、使用和保護您的個人資訊，請參閱我們的「隱私權政策」。") // TODO: Link to Privacy Policy View
                }
                
                SectionView(title: "6. 免責聲明") {
                    Text("本 App 按「現狀」提供，我們不對服務的及時性、安全性、準確性或可靠性作任何明示或暗示的保證。您同意自行承擔使用本 App 的所有風險。")
                }

                SectionView(title: "7. 條款修改") {
                    Text("我們保留隨時修改本條款的權利。修改後的條款將公布於本 App 中，並自公布時生效。建議您定期查閱。若您在修改後繼續使用本 App，視為您已接受修改後的條款。")
                }

                SectionView(title: "8. 聯絡我們") {
                     Text("若您對本條款有任何疑問，請透過 App 內的「意見回饋」功能與我們聯繫。") // TODO: Link to Feedback View
                }
                
                Text("最近更新日期：[請填寫更新日期]")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.top)

            }
            .padding()
        }
        .navigationTitle("服務條款")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// Helper Section View (如果還沒有，可以從 SettingsView 複製或創建一個)
// struct SectionView<Content: View>: View {
//     let title: String
//     let content: Content
// 
//     init(title: String, @ViewBuilder content: () -> Content) {
//         self.title = title
//         self.content = content()
//     }
// 
//     var body: some View {
//         VStack(alignment: .leading, spacing: 8) {
//             Text(title)
//                 .font(.title3)
//                 .fontWeight(.semibold)
//             content
//                 .font(.body)
//                 .foregroundColor(.secondary)
//         }
//         .padding(.bottom)
//     }
// }


struct TermsView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            TermsView()
        }
    }
}
