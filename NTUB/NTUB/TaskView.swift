import SwiftUI

struct TaskView: View {
    @State private var selectedCategory: TaskCategory? = nil
    @State private var showingAddTask = false
    @State private var showingSchedule = false
    @State private var isTimerRunning = false
    @State private var remainingTime: TimeInterval = 25 * 60 // 25分鐘
    @State private var selectedTask: Task? = nil
    @State private var weatherInfo: String = "晴天 26°C"
    
    // 模擬資料
    @State private var tasks = [
        Task(title: "準備統計學報告", description: "第五章課堂報告", category: .study, estimatedDuration: 25 * 60),
        Task(title: "閱讀經濟學教材", description: "第三章預習", category: .reading, estimatedDuration: 30 * 60),
        Task(title: "體育課", description: "籃球課程", category: .exercise, estimatedDuration: 45 * 60),
        Task(title: "小組專題", description: "資料庫設計", category: .work, estimatedDuration: 120 * 60)
    ]
    
    var filteredTasks: [Task] {
        if let category = selectedCategory {
            return tasks.filter { $0.category == category }
        }
        return tasks
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 天氣與課程提醒
                WeatherReminderView(weatherInfo: weatherInfo)
                
                // 類別選擇區
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        Button(action: { showingSchedule = true }) {
                            HStack {
                                Image(systemName: "calendar")
                                Text("課表")
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(20)
                        }
                        
                        CategoryButton(title: "全部", icon: "list.bullet", isSelected: selectedCategory == nil) {
                            selectedCategory = nil
                        }
                        
                        ForEach(TaskCategory.allCases, id: \.self) { category in
                            CategoryButton(
                                title: category.rawValue,
                                icon: category.icon,
                                isSelected: selectedCategory == category
                            ) {
                                selectedCategory = category
                            }
                        }
                    }
                    .padding()
                }
                .background(Color(.systemBackground))
                .overlay(
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(Color(.systemGray5)),
                    alignment: .bottom
                )
                
                // 任務列表
                if isTimerRunning {
                    // 專注計時器視圖
                    FocusTimerView(
                        isRunning: $isTimerRunning,
                        remainingTime: $remainingTime,
                        task: selectedTask
                    )
                } else {
                    // 任務列表視圖
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(filteredTasks) { task in
                                TaskCard(task: task) {
                                    selectedTask = task
                                    isTimerRunning = true
                                    remainingTime = task.estimatedDuration
                                }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("課表與任務")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddTask = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingSchedule) {
                ScheduleView()
            }
            .sheet(isPresented: $showingAddTask) {
                AddTaskView()
            }
        }
    }
}

// 天氣提醒視圖
struct WeatherReminderView: View {
    let weatherInfo: String
    
    var body: some View {
        HStack {
            Image(systemName: "cloud.sun.fill")
                .foregroundColor(.orange)
            Text(weatherInfo)
            Spacer()
            Text("下節課：程式設計 @E201")
                .foregroundColor(.blue)
        }
        .padding()
        .background(Color(.systemGray6))
    }
}

// 課表視圖
struct ScheduleView: View {
    var body: some View {
        Text("課表視圖")
            .navigationTitle("我的課表")
    }
}

// 新增任務視圖
struct AddTaskView: View {
    var body: some View {
        Text("新增任務")
            .navigationTitle("新增任務")
    }
}

// 類別按鈕元件
struct CategoryButton: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(isSelected ? Color.blue : Color(.systemGray6))
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
        }
    }
}

// 任務卡片元件
struct TaskCard: View {
    let task: Task
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Image(systemName: task.category.icon)
                        .foregroundColor(Color(task.category.color))
                    Text(task.title)
                        .font(.headline)
                    Spacer()
                    Image(systemName: "play.circle.fill")
                        .foregroundColor(.blue)
                        .imageScale(.large)
                }
                
                if let description = task.description {
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                
                HStack {
                    Text("預計時間：\(Int(task.estimatedDuration / 60))分鐘")
                        .font(.caption)
                        .foregroundColor(.gray)
                    Spacer()
                    Text(task.category.rawValue)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(task.category.color).opacity(0.2))
                        .cornerRadius(8)
                }
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// 專注計時器視圖
struct FocusTimerView: View {
    @Binding var isRunning: Bool
    @Binding var remainingTime: TimeInterval
    let task: Task?
    
    let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            if let task = task {
                Text(task.title)
                    .font(.title2)
                    .fontWeight(.medium)
            }
            
            Text(timeString(from: remainingTime))
                .font(.system(size: 60, weight: .bold, design: .rounded))
                .monospacedDigit()
            
            HStack(spacing: 20) {
                Button(action: { isRunning = false }) {
                    Image(systemName: "xmark.circle.fill")
                        .resizable()
                        .frame(width: 44, height: 44)
                        .foregroundColor(.red)
                }
                
                Button(action: {
                    // TODO: 暫停/繼續計時
                }) {
                    Image(systemName: "pause.circle.fill")
                        .resizable()
                        .frame(width: 60, height: 60)
                        .foregroundColor(.blue)
                }
                
                Button(action: {
                    // TODO: 完成任務
                }) {
                    Image(systemName: "checkmark.circle.fill")
                        .resizable()
                        .frame(width: 44, height: 44)
                        .foregroundColor(.green)
                }
            }
            
            Spacer()
        }
        .padding()
        .onReceive(timer) { _ in
            if remainingTime > 0 {
                remainingTime -= 1
            }
        }
    }
    
    private func timeString(from timeInterval: TimeInterval) -> String {
        let minutes = Int(timeInterval) / 60
        let seconds = Int(timeInterval) % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
}

#Preview {
    TaskView()
} 