import SwiftUI

struct HomeView: View {

    // --- Mock Data (模擬資料) ---
    // 實際應用中，這些資料會從 ViewModel 或其他來源取得
    @State private var currentUser = User(username: "學習者") // 假設的使用者名稱
    @State private var todayStats = DailyStats(date: Date(), totalStudyTime: 3600 + 1800 + 300, studySessions: 3) // 1h 35m
    @State private var learningPlans = [
        LearningPlan(title: "完成 Swift 基礎語法", deadline: Calendar.current.date(byAdding: .day, value: 2, to: Date())),
        LearningPlan(title: "閱讀 SwiftUI 文件第一章", isCompleted: true),
        LearningPlan(title: "準備期中專案簡報", deadline: Calendar.current.date(byAdding: .day, value: 7, to: Date()))
    ]
    @State private var studyPartners = [
        StudyPartner(username: "Alice", isOnline: true),
        StudyPartner(username: "Bob", isOnline: false),
        StudyPartner(username: "Charlie", isOnline: true)
    ]
    @State private var calendarEvents = [
        CalendarEvent(title: "小組討論", startDate: Calendar.current.date(byAdding: .hour, value: 2, to: Date())!, endDate: Calendar.current.date(byAdding: .hour, value: 3, to: Date())!, color: Color.orange),
        CalendarEvent(title: "演算法複習", startDate: Calendar.current.date(byAdding: .day, value: 1, to: Date())!, endDate: Calendar.current.date(byAdding: .day, value: 1, to: Date())!, color: Color.green)
    ]
    // --- End Mock Data ---

    var body: some View {
        NavigationView { // 加入 NavigationView 以便放置標題
            ScrollView { // 使用 ScrollView 讓內容可以滾動
                VStack(alignment: .leading, spacing: 25) {
                    
                    // 1. 歡迎標語
                    Text("你好，\(currentUser.username)！")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .padding(.bottom, 5)

                    // 2. 今日統計
                    GroupBox("今日統計") { // 使用 GroupBox 來區塊化
                        HStack(spacing: 20) {
                            StatItem(value: todayStats.totalStudyTime.formattedDuration(), label: "專注時間")
                            Divider()
                            StatItem(value: "\(todayStats.studySessions)", label: "學習次數")
                        }
                        .padding(.vertical, 5)
                    }
                    
                    // 3. 行事曆 (Placeholder)
                    GroupBox("行事曆") {
                        VStack(alignment: .leading) {
                            Text("今日: \(Date(), style: .date)")
                                .font(.headline)
                                .padding(.bottom, 5)
                            // TODO: 在這裡加入實際的行事曆元件
                            Text("未來的行事曆元件...")
                                .foregroundColor(.gray)
                                .frame(maxWidth: .infinity, minHeight: 100)
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                        }
                    }

                    // 4. 學習計畫
                    GroupBox("學習計畫") {
                        VStack(alignment: .leading) {
                            ForEach(learningPlans) { plan in
                                LearningPlanRow(plan: plan)
                                if plan.id != learningPlans.last?.id {
                                    Divider()
                                }
                            }
                            // 可以加上「查看更多」按鈕
                        }
                    }

                    // 5. 學習夥伴
                    GroupBox("學習夥伴") {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 15) {
                                ForEach(studyPartners) { partner in
                                    StudyPartnerIcon(partner: partner)
                                }
                            }
                            .padding(.vertical, 5)
                        }
                    }
                    
                    Spacer() // 將內容推到頂部
                }
                .padding() // 為 VStack 加上 padding
            }
            .navigationTitle("首頁") // 設定 Navigation Bar 標題
            .navigationBarTitleDisplayMode(.inline) // 可以設為 .large 或 .inline
        }
    }
}

// --- Helper Views (輔助視圖) ---

// 用於顯示單個統計數據
struct StatItem: View {
    let value: String
    let label: String
    
    var body: some View {
        VStack {
            Text(value)
                .font(.title2)
                .fontWeight(.semibold)
            Text(label)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity) // 讓項目平均分配寬度
    }
}

// 用於顯示單個學習計畫
struct LearningPlanRow: View {
    let plan: LearningPlan
    
    var body: some View {
        HStack {
            Image(systemName: plan.isCompleted ? "checkmark.circle.fill" : "circle")
                .foregroundColor(plan.isCompleted ? .green : .gray)
            Text(plan.title)
                .strikethrough(plan.isCompleted, color: .gray) // 完成的加上刪除線
                .foregroundColor(plan.isCompleted ? .gray : .primary)
            Spacer()
            if let deadline = plan.deadline {
                Text(deadline, style: .date)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
        .padding(.vertical, 8)
    }
}

// 用於顯示學習夥伴頭像
struct StudyPartnerIcon: View {
    let partner: StudyPartner
    
    var body: some View {
        VStack {
            ZStack(alignment: .bottomTrailing) {
                // 使用系統圖標作為 Placeholder
                Image(systemName: "person.circle.fill") 
                    .resizable()
                    .scaledToFit()
                    .frame(width: 50, height: 50)
                    .foregroundColor(.gray)
                    // 如果有 profileImageURL，可以使用 AsyncImage 載入
                
                // 在線狀態指示燈
                Circle()
                    .fill(partner.isOnline ? Color.green : Color.gray)
                    .frame(width: 12, height: 12)
                    .overlay(Circle().stroke(Color.white, lineWidth: 2))
            }
            Text(partner.username)
                .font(.caption)
        }
    }
}

// --- Preview ---
#Preview {
    // 在 Preview 中可以直接創建 HomeView
    // TabView { // 可以預覽在 TabView 中的樣子
        HomeView()
    //    .tabItem { Label("首頁", systemImage: "house.fill") }
    // }
} 