import SwiftUI
// test
// MARK: - Edit Course View
struct EditCourseView: View {
    @Environment(\.presentationMode) var presentationMode
    let originalCourse: ScheduleCourse
    @Binding var courses: [ScheduleCourse]

    // --- State Variables for the Form (Initialized from originalCourse) ---
    @State private var courseName: String
    @State private var teacher: String // Assuming teacher might be added to ScheduleCourse later
    @State private var location: String
    @State private var selectedDay: Weekday
    @State private var startTime: Date
    @State private var endTime: Date
    @State private var selectedColor: Color
    @State private var notes: String // Assuming notes might be added
    
    @State private var showingDeleteAlert = false

    // --- Available Colors (Same as AddCourseView) ---
    let colors: [Color] = [.blue.opacity(0.7), .green.opacity(0.7), .orange.opacity(0.7), .red.opacity(0.7), .purple.opacity(0.7), .gray.opacity(0.7)]

    // --- Initializer ---
    init(originalCourse: ScheduleCourse, courses: Binding<[ScheduleCourse]>) {
        self.originalCourse = originalCourse
        self._courses = courses

        // Initialize @State vars
        _courseName = State(initialValue: originalCourse.name)
        _teacher = State(initialValue: "") // Placeholder, update if teacher is added to model
        _location = State(initialValue: originalCourse.location)
        _selectedDay = State(initialValue: originalCourse.day)
        // Convert start/end hour back to Date for DatePicker
        _startTime = State(initialValue: Calendar.current.date(bySettingHour: originalCourse.startTime, minute: 0, second: 0, of: Date())!)
        _endTime = State(initialValue: Calendar.current.date(bySettingHour: originalCourse.endTime, minute: 0, second: 0, of: Date())!)
        _selectedColor = State(initialValue: originalCourse.color)
        _notes = State(initialValue: "") // Placeholder, update if notes is added to model
    }

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
                    DatePicker("開始時間", selection: $startTime, displayedComponents: .hourAndMinute)
                    DatePicker("結束時間", selection: $endTime, displayedComponents: .hourAndMinute)
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
                     TextField("輸入備註 (選填)", text: $notes, axis: .vertical)
                         .lineLimit(3...)
                }

                // --- Delete Button Section ---
                Section {
                    Button(role: .destructive) {
                        showingDeleteAlert = true
                    } label: {
                        Text("刪除課程")
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                }
            }
            .navigationTitle("編輯課程")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("儲存") {
                        saveChanges()
                    }
                    .disabled(courseName.isEmpty)
                }
            }
            .alert("確認刪除", isPresented: $showingDeleteAlert) {
                Button("確認刪除", role: .destructive) { deleteCourse() }
                Button("取消", role: .cancel) { }
            } message: {
                Text("您確定要刪除此課程嗎？")
            }
        }
    }
    
    private func saveChanges() {
        let startHour = Calendar.current.component(.hour, from: startTime)
        let endHour = Calendar.current.component(.hour, from: endTime)
        
        guard !courseName.isEmpty else { return }
        guard endHour > startHour else { /* show alert */ return }
        
        if let index = courses.firstIndex(where: { $0.id == originalCourse.id }) {
            courses[index].name = courseName
            courses[index].location = location
            courses[index].day = selectedDay
            courses[index].startTime = startHour
            courses[index].endTime = endHour
            courses[index].color = selectedColor
        } else {
            print("Error: Could not find course to update.")
        }
        presentationMode.wrappedValue.dismiss()
    }

    private func deleteCourse() {
        if let index = courses.firstIndex(where: { $0.id == originalCourse.id }) {
            courses.remove(at: index)
        } else {
            print("Error: Could not find course to delete.")
        }
        presentationMode.wrappedValue.dismiss()
    }
}

// MARK: - Preview (Requires sample data)
struct EditCourseView_Previews: PreviewProvider {
    // Create dummy data for preview
    @State static var previewCourses: [ScheduleCourse] = [
        ScheduleCourse(name: "預覽課", location: "A101", day: .monday, startTime: 9, endTime: 11, color: .purple.opacity(0.7))
    ]
    static var previewCourse = previewCourses[0]

    static var previews: some View {
        EditCourseView(originalCourse: previewCourse, courses: $previewCourses)
    }
} 