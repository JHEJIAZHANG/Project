import SwiftUI

// MARK: - Data Models for Timetable
struct ScheduleCourse: Identifiable {
    let id = UUID()
    let name: String
    let location: String
    let day: Weekday // 星期幾
    let startTime: Int // 開始小時 (24小時制, e.g., 8, 10, 13)
    let endTime: Int   // 結束小時 (e.g., 10, 12, 15) - 不含結束時間點
    let color: Color
}

enum Weekday: Int, CaseIterable, Identifiable {
    case monday = 1, tuesday, wednesday, thursday, friday //, saturday, sunday
    var id: Int { self.rawValue }

    var shortName: String {
        switch self {
        case .monday: return "一"
        case .tuesday: return "二"
        case .wednesday: return "三"
        case .thursday: return "四"
        case .friday: return "五"
        // case .saturday: return "六"
        // case .sunday: return "日"
        }
    }
}

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
    
    // 課表時間範圍和格子高度
    let hourHeight: CGFloat = 60
    let startHour = 8
    let endHour = 17 // 顯示到 17:00

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 1. 頂部操作欄
                HStack {
                    Button("本週") { /* TODO: Implement week switching */ }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                        .font(.subheadline)
                    
                    Spacer()
                    
                    Button { /* TODO: Implement search */ } label: {
                        Image(systemName: "magnifyingglass")
                            .font(.title2)
                    }
                    .padding(.horizontal, 5)
                    
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
                                    CourseBlockView(course: course)
                                        .frame(width: dayWidth - 4, height: CGFloat(course.endTime - course.startTime) * hourHeight - 4) // 減去 padding
                                        .position(
                                            x: calculateXPosition(for: course.day, dayWidth: dayWidth),
                                            y: calculateYPosition(for: course.startTime) + CGFloat(course.endTime - course.startTime) * hourHeight / 2 // 定位到中心
                                        )
                                }
                            }
                            .padding(.top, hourHeight / 2) // 同步課程格子的起始 Y
                        }
                    }
                    // 設定一個最小高度，防止 ScrollView 內容過少時塌陷
                    .frame(minHeight: CGFloat(endHour - startHour) * hourHeight + hourHeight)
                }
            }
            .navigationTitle("我的課表")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarHidden(true) // 根據頂部操作欄設計，隱藏原生導航欄
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
struct AddCourseView: View {
    @Environment(\.presentationMode) var presentationMode
    @Binding var courses: [ScheduleCourse] // 接收綁定

    // 表單狀態
    @State private var courseName: String = ""
    @State private var teacher: String = "" // 原型有，補充
    @State private var location: String = ""
    @State private var selectedDay: Weekday = .monday
    @State private var startTime: Date = Calendar.current.date(bySettingHour: 8, minute: 0, second: 0, of: Date())!
    @State private var endTime: Date = Calendar.current.date(bySettingHour: 10, minute: 0, second: 0, of: Date())!
    @State private var selectedColor: Color = .blue.opacity(0.7)
    @State private var notes: String = ""

    let colors: [Color] = [.blue.opacity(0.7), .green.opacity(0.7), .orange.opacity(0.7), .red.opacity(0.7), .purple.opacity(0.7), .gray.opacity(0.7)]

    var body: some View {
         NavigationView {
             Form {
                 Section("課程資訊") {
                     TextField("課程名稱", text: $courseName)
                     TextField("教師", text: $teacher)
                     TextField("教室", text: $location)
                 }

                 Section("時間與星期") {
                     Picker("星期", selection: $selectedDay) {
                         ForEach(Weekday.allCases) { day in
                             Text(day.shortName).tag(day)
                         }
                     }
                     // 使用 DatePicker 選擇時間
                     DatePicker("開始時間", selection: $startTime, displayedComponents: .hourAndMinute)
                     DatePicker("結束時間", selection: $endTime, displayedComponents: .hourAndMinute)
                     // TODO: 添加時間驗證 (結束時間 > 開始時間)
                 }
                 
                 Section("外觀") {
                     HStack {
                         Text("顏色")
                         Spacer()
                         ForEach(colors, id: \.self) { color in
                             Circle()
                                 .fill(color)
                                 .frame(width: 25, height: 25)
                                 .overlay(
                                     Circle().stroke(selectedColor == color ? Color.primary : Color.clear, lineWidth: 2)
                                 )
                                 .onTapGesture {
                                     selectedColor = color
                                 }
                         }
                     }
                 }
                 
                 Section("備註") {
                      TextField("輸入備註 (選填)", text: $notes, axis: .vertical) // 允許多行
                          .lineLimit(3...)
                 }

                 Section {
                     Button("添加課程") {
                         addCourse()
                     }
                 }
             }
             .navigationTitle("添加課程")
             .navigationBarItems(leading: Button("取消") {
                 presentationMode.wrappedValue.dismiss()
             })
         }
    }
    
    private func addCourse() {
        // 從 DatePicker 獲取小時
        let startHour = Calendar.current.component(.hour, from: startTime)
        let endHour = Calendar.current.component(.hour, from: endTime) // 假設結束時間代表 block 結束點
        
        // 簡單驗證
        guard !courseName.isEmpty else { /* show alert */ return }
        guard endHour > startHour else { /* show alert */ return }
        
        let newCourse = ScheduleCourse(
            name: courseName,
            location: location,
            day: selectedDay,
            startTime: startHour,
            endTime: endHour,
            color: selectedColor
            // 可以添加 teacher 和 notes 到 ScheduleCourse 模型中
        )
        courses.append(newCourse)
        presentationMode.wrappedValue.dismiss()
    }
}


// MARK: - Preview
#Preview {
    TimetableView()
} 