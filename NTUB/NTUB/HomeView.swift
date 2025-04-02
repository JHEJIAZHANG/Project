import SwiftUI

// --- 新增：模擬資料模型 - REMOVE THESE ---
// 課程模型
struct Course: Identifiable {
    let id = UUID()
    let name: String
    let time: String
    let location: String
    let color: Color // 可選，用於課表顏色等
}

// 待辦事項模型 - REMOVE THIS
/*
struct TodoItem: Identifiable {
    let id = UUID()
    let title: String
    let deadline: String // 簡化為字串表示
    let priority: Priority
    var isCompleted: Bool = false

    enum Priority {
        case high, medium, low
        
        var color: Color {
            switch self {
            case .high: return .red
            case .medium: return .orange
            case .low: return .blue
            }
        }
    }
}
*/
// --- Models Removed ---

struct HomeView: View {

    // --- Mock Data (符合新設計) ---
    @State private var username = "陳同學" // 原型中的使用者名稱
    // 今日課程假資料
    @State private var todayCourses: [Course] = [
        Course(name: "資料庫系統", time: "10:00 - 12:00", location: "E201教室", color: .blue.opacity(0.7)),
        Course(name: "網頁程式設計", time: "13:30 - 15:30", location: "E401教室", color: .green.opacity(0.7))
    ]
    // 待辦事項假資料 (現在使用 Models/TodoItem.swift)
    @State private var upcomingTodos: [TodoItem] = [
        // Use the full initializer from Models/TodoItem.swift
        TodoItem(title: "資料庫系統作業", category: .study, dueDate: Calendar.current.date(bySettingHour: 23, minute: 59, second: 0, of: Date()), priority: .high),
        TodoItem(title: "購買計算機概論教科書", category: .life, dueDate: Calendar.current.date(byAdding: .day, value: 2, to: Date()), priority: .medium)
    ]
    // --- End Mock Data ---

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {

                    // 1. 歡迎標語和用戶頭像 + 課表入口
                    HStack {
                        Text("你好，\\(username)")
                            .font(.system(size: 24, weight: .semibold))
                        Spacer()
                        
                        // 新增：課表入口按鈕
                        NavigationLink(destination: TimetableView()) {
                            Image(systemName: "calendar")
                                .font(.title2)
                                .foregroundColor(.blue)
                                .padding(8) // Add padding to increase tap area
                                .background(Color.blue.opacity(0.1))
                                .clipShape(Circle())
                        }
                        .padding(.trailing, 5)
                        
                        Image(systemName: "person.circle.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 40, height: 40)
                            .foregroundColor(.gray.opacity(0.5))
                    }

                    // 2. 天氣提醒
                    HStack(spacing: 15) {
                        Image(systemName: "cloud.rain.fill") // 天氣圖示 (根據實際情況更換)
                            .font(.system(size: 24))
                            .foregroundColor(.blue)
                        VStack(alignment: .leading) {
                            Text("今日天氣提醒")
                                .font(.headline)
                            Text("今天有雨，記得帶傘去上課！") // 提醒內容 (可動態生成)
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                        Spacer() // 將內容推向左側
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1)) // 淡藍色背景
                    .cornerRadius(12)

                    // 3. 今日課程
                    VStack(alignment: .leading, spacing: 10) {
                        Text("今日課程")
                            .font(.title2)
                            .fontWeight(.semibold)
                        
                        // 使用 ForEach 顯示課程卡片
                        ForEach(todayCourses) { course in
                            CourseCardView(course: course)
                        }
                    }

                    // 4. 待辦事項
                    VStack(alignment: .leading, spacing: 10) {
                        Text("待辦事項")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .padding(.top) // 與上方區塊增加間距

                        // 使用 ForEach 顯示待辦事項卡片
                        ForEach(upcomingTodos) { todo in
                            TodoCardView(todo: todo)
                        }
                    }

                    Spacer() // 將內容推到頂部
                }
                .padding() // 為最外層 VStack 加上 padding
            }
            .navigationBarHidden(true) // 隱藏導航欄
        }
    }
}

// --- 輔助視圖 (符合新設計) ---

// 課程卡片視圖
struct CourseCardView: View {
    let course: Course // This uses the 'Course' struct defined above (temporarily)

    var body: some View {
        VStack(alignment: .leading) {
            HStack {
                Text(course.name)
                    .font(.headline)
                Spacer()
                Text(course.time)
                    .font(.subheadline)
                    .foregroundColor(.blue) // 時間用藍色表示
            }
            HStack {
                Image(systemName: "mappin.and.ellipse")
                Text(course.location)
            }
            .font(.subheadline)
            .foregroundColor(.gray)
        }
        .padding()
        .background(Color(.systemGray6)) // 卡片背景色
        .cornerRadius(12)
    }
}

// 待辦事項卡片視圖
struct TodoCardView: View {
    let todo: TodoItem // This now uses the global Models/TodoItem.swift

    var body: some View {
        HStack(spacing: 15) {
            // 優先級指示器 (圓點)
            Circle()
                .fill(todo.priority.color)
                .frame(width: 10, height: 10)

            // 方框 (模擬原型中的方框)
            Rectangle()
                .stroke(todo.priority.color, lineWidth: 2)
                .frame(width: 20, height: 20)
                .cornerRadius(4)
                // TODO: 添加點擊完成的功能

            VStack(alignment: .leading) {
                Text(todo.title)
                    .font(.headline)
                    .strikethrough(todo.isCompleted) // 完成加刪除線
                Text(todo.deadlineString)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            Spacer() // 將內容推向左側
        }
        .padding()
        .background(Color(.systemGray6)) // 卡片背景色
        .cornerRadius(12)
    }
}


// --- 移除舊的 Helper Views ---
/*
struct StatItem: View { ... }
struct LearningPlanRow: View { ... }
struct StudyPartnerIcon: View { ... }
*/

// --- Preview ---
#Preview {
    // 預覽 HomeView
    HomeView()
    // 可以包在 TabView 中預覽
    /*
    TabView {
        HomeView()
            .tabItem { Label("首頁", systemImage: "house.fill") }
    }
    */
} 