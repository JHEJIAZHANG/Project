import SwiftUI
import Charts

struct ChartView: View {
    @State private var weeklyStats = StudyStats.mockWeeklyData()
    @State private var categoryStats = StudyStats.mockCategoryData()
    @State private var selectedTimeRange = TimeRange.week
    
    enum TimeRange {
        case day, week, month
        
        var title: String {
            switch self {
            case .day: return "今日"
            case .week: return "本週"
            case .month: return "本月"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // 時間範圍選擇器
                    Picker("時間範圍", selection: $selectedTimeRange) {
                        Text("今日").tag(TimeRange.day)
                        Text("本週").tag(TimeRange.week)
                        Text("本月").tag(TimeRange.month)
                    }
                    .pickerStyle(.segmented)
                    .padding(.horizontal)
                    
                    // 總覽卡片
                    VStack(spacing: 15) {
                        Text(selectedTimeRange.title + "總覽")
                            .font(.headline)
                        
                        HStack(spacing: 30) {
                            StatCard(
                                title: "專注時間",
                                value: "12.5小時",
                                icon: "clock.fill",
                                color: .blue
                            )
                            
                            StatCard(
                                title: "完成任務",
                                value: "24個",
                                icon: "checkmark.circle.fill",
                                color: .green
                            )
                        }
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
                    .padding(.horizontal)
                    
                    // 每日專注時間圖表
                    ChartCard(title: "每日專注時間") {
                        Chart(weeklyStats, id: \.date) { stat in
                            BarMark(
                                x: .value("日期", stat.date, unit: .day),
                                y: .value("時間", stat.focusTime / 3600)
                            )
                            .foregroundStyle(Color.blue.gradient)
                        }
                        .chartXAxis {
                            AxisMarks(values: .stride(by: .day)) { value in
                                AxisValueLabel(format: .dateTime.weekday())
                            }
                        }
                        .chartYAxis {
                            AxisMarks(position: .leading)
                        }
                    }
                    
                    // 類別分佈圖表
                    ChartCard(title: "類別分佈") {
                        Chart(categoryStats, id: \.category) { stat in
                            SectorMark(
                                angle: .value("時間", stat.focusTime),
                                innerRadius: .ratio(0.618),
                                angularInset: 1.5
                            )
                            .foregroundStyle(by: .value("類別", stat.category.rawValue))
                        }
                    }
                    .frame(height: 250)
                    
                    // 完成任務統計
                    ChartCard(title: "完成任務統計") {
                        Chart(weeklyStats, id: \.date) { stat in
                            LineMark(
                                x: .value("日期", stat.date, unit: .day),
                                y: .value("任務數", stat.completedTasks)
                            )
                            .foregroundStyle(Color.green.gradient)
                            
                            PointMark(
                                x: .value("日期", stat.date, unit: .day),
                                y: .value("任務數", stat.completedTasks)
                            )
                            .foregroundStyle(Color.green)
                        }
                        .chartXAxis {
                            AxisMarks(values: .stride(by: .day)) { value in
                                AxisValueLabel(format: .dateTime.weekday())
                            }
                        }
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle("統計")
            .navigationBarTitleDisplayMode(.inline)
            .background(Color(.systemGroupedBackground))
        }
    }
}

// 統計卡片元件
struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title3)
                .fontWeight(.semibold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(10)
    }
}

// 圖表卡片元件
struct ChartCard<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
            
            content
                .frame(height: 200)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
}

#Preview {
    ChartView()
} 