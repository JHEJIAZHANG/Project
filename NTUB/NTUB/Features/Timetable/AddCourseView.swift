import SwiftUI

// MARK: - Add Course View
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

// MARK: - Preview (Optional, might need adjustments)
#if DEBUG
struct AddCourseView_Previews: PreviewProvider {
    @State static var previewCourses: [ScheduleCourse] = []
    static var previews: some View {
        AddCourseView(courses: $previewCourses)
    }
}
#endif 