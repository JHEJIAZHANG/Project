import SwiftUI

// MARK: - Data Models for Timetable
// Removed ScheduleCourse and Weekday definitions from here

// MARK: - Main Timetable View
struct TimetableView: View {
    // --- Mock Data ---
    @State private var courses: [ScheduleCourse] = [
        ScheduleCourse(name: "資料庫系統", location: "E201", day: .monday, startTime: 10, endTime: 12, color: .blue.opacity(0.7)),
        ScheduleCourse(name: "英文", location: "E301", day: .tuesday, startTime: 13, endTime: 14, color: .green.opacity(0.7)),
        ScheduleCourse(name: "網頁程式", location: "E401", day: .wednesday, startTime: 10, endTime: 12, color: .orange.opacity(0.7)),
        ScheduleCourse(name: "行動應用開發", location: "E502", day: .thursday, startTime: 9, endTime: 11, color: .red.opacity(0.7)),
        // 可以添加更多課程...
    ]
    
    @State private var showingAddCourseSheet = false
    @State private var showingShareSheet = false
    @State private var displayedWeekStartDate: Date = Date().startOfWeek ?? Date()
    @State private var courseToEdit: ScheduleCourse? = nil
    
    // 課表時間範圍和格子高度
    let hourHeight: CGFloat = 60
    let startHour = 8
    let endHour = 17 // 顯示到 17:00

    // --- 新增計算屬性：顯示的週日期範圍 ---
    var displayedWeekRangeString: String {
        let calendar = Calendar.current
        let startDate = displayedWeekStartDate
        // 計算星期五的日期 (週一 + 4 天)
        guard let endDate = calendar.date(byAdding: .day, value: 4, to: startDate) else {
            return "日期錯誤" 
        }

        let formatter = DateFormatter()
        formatter.dateFormat = "MM/dd" // 格式化為 月/日

        let startString = formatter.string(from: startDate)
        let endString = formatter.string(from: endDate)

        return "\(startString) - \(endString)"
    }
    // --- 計算屬性結束 ---

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 1. 頂部操作欄
                HStack {
                    Button("本週") {
                        print("「本週」按鈕點擊")
                        let currentWeekStart = Date().startOfWeek ?? Date()
                        displayedWeekStartDate = currentWeekStart
                        // TODO: 後續需要確保課表主體根據 displayedWeekStartDate 重新篩選/繪製
                    }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                        .font(.subheadline)
                    
                    // --- 新增日期範圍顯示 ---
                    Text(displayedWeekRangeString)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .padding(.leading, 8) 
                    // --- 日期範圍顯示結束 ---
                    
                    Spacer()
                    
                    Button { showingShareSheet = true } label: {
                        Image(systemName: "square.and.arrow.up")
                            .font(.title2)
                    }
                    .padding(.horizontal, 5)
                    
                    Button { showingAddCourseSheet = true } label: {
                        Image(systemName: "plus")
                            .font(.title2)
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 10)
                .background(Color(.systemBackground)) // Match background
                // .border(Color.gray.opacity(0.2), width: 0.5) // Optional border

                // 2. 星期標頭
                HStack(spacing: 0) {
                    // 時間軸的空白佔位
                    Spacer().frame(width: 40) // 與時間軸寬度一致
                    ForEach(Weekday.allCases) { day in
                        Text(day.shortName)
                            .font(.caption)
                            .fontWeight(.medium)
                            .frame(maxWidth: .infinity)
                            .frame(height: 30) // 固定標頭高度
                            .background(Color(.systemGray6))
                    }
                }
                .background(Color(.systemGray5)) // Header background

                // 3. 課表主體 (ScrollView + 時間軸 + 課程格子)
                ScrollView {
                    ZStack(alignment: .topLeading) {
                        // 背景時間線 (水平)
                        VStack(spacing: 0) {
                            ForEach(startHour..<endHour, id: \.self) { hour in
                                Divider()
                                    .frame(height: hourHeight)
                                    .offset(y: -hourHeight / 2) // 將線條移到格子中間偏上
                            }
                        }
                        .padding(.leading, 40) // 避開時間軸

                        // 背景垂直線 (分隔每天)
                        HStack(spacing: 0) {
                            Spacer().frame(width: 40) // 時間軸佔位
                             ForEach(Weekday.allCases) { day in
                                 Divider()
                                     .frame(maxWidth: .infinity)
                             }
                        }
                        
                        HStack(spacing: 0) {
                            // 時間軸
                            VStack(spacing: 0) {
                                ForEach(startHour..<endHour, id: \.self) { hour in
                                    Text(String(format: "%02d:00", hour))
                                        .font(.caption2)
                                        .foregroundColor(.gray)
                                        .frame(width: 40, height: hourHeight, alignment: .top)
                                        .offset(y: -6) // 向上微調，對齊線條
                                }
                                Spacer() // 填滿剩餘空間
                            }
                            .frame(width: 40)
                            .padding(.top, hourHeight / 2) // 讓第一個時間點對齊第一條線下方

                            // 課程格子 (使用 GeometryReader 計算位置)
                            GeometryReader { geometry in
                                let totalWidth = geometry.size.width
                                let dayWidth = totalWidth / CGFloat(Weekday.allCases.count)
                                
                                ForEach(courses) { course in
                                    Button { 
                                        courseToEdit = course
                                    } label: {
                                        CourseBlockView(course: course)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                    .frame(width: dayWidth - 4, height: CGFloat(course.endTime - course.startTime) * hourHeight - 4)
                                    .position(
                                        x: calculateXPosition(for: course.day, dayWidth: dayWidth),
                                        y: calculateYPosition(for: course.startTime) + CGFloat(course.endTime - course.startTime) * hourHeight / 2
                                    )
                                }
                            }
                            .padding(.top, hourHeight / 2)
                        }
                    }
                    // 設定一個最小高度，防止 ScrollView 內容過少時塌陷
                    .frame(minHeight: CGFloat(endHour - startHour) * hourHeight + hourHeight)
                }
            }
            .navigationTitle("我的課表")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarHidden(true) // 根據頂部操作欄設計，隱藏原生導航欄
            .sheet(item: $courseToEdit) { course in
                EditCourseView(originalCourse: course, courses: $courses)
            }
            .sheet(isPresented: $showingAddCourseSheet) {
                 AddCourseView(courses: $courses) // 傳遞 courses 綁定
            }
            .sheet(isPresented: $showingShareSheet) {
                 ShareScheduleView() // 稍後創建此視圖
            }
        }
    }

    // 計算課程 X 位置 (根據星期)
    private func calculateXPosition(for day: Weekday, dayWidth: CGFloat) -> CGFloat {
        // day.rawValue 從 1 開始，所以減 1
        // + 0.5 將中心點移到格子中間
        return (CGFloat(day.rawValue - 1) + 0.5) * dayWidth
    }

    // 計算課程 Y 位置 (根據開始時間)
    private func calculateYPosition(for startHourOfDay: Int) -> CGFloat {
        // 相對於課表開始時間的偏移小時數
        let hourOffset = CGFloat(startHourOfDay - startHour)
        return hourOffset * hourHeight
    }
}

// MARK: - Course Block View
struct CourseBlockView: View {
    let course: ScheduleCourse

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(course.name)
                .font(.system(size: 12, weight: .semibold))
                .lineLimit(course.endTime - course.startTime > 1 ? 2 : 1) // 根據高度調整行數
            Text(course.location)
                .font(.system(size: 10))
                .foregroundColor(.white.opacity(0.8))
                .lineLimit(1)
        }
        .padding(4)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading) // 確保填滿並靠上對齊
        .background(course.color)
        .foregroundColor(.white)
        .cornerRadius(6)
        .clipped() // 防止文字溢出圓角
    }
}

// MARK: - Add Course View (Placeholder)
// Removed AddCourseView struct definition from here

// MARK: - Preview
#Preview {
    TimetableView()
} 

// MARK: - Date Extension for Start of Week
// Removed Date extension from here 