import SwiftUI

struct EditTaskView: View {
    @Environment(\.dismiss) var dismiss // 用於關閉視圖

    // 從 TaskView 傳入的原始任務資料 (不可變) 和 todos 陣列的綁定
    let originalTask: TodoItem
    @Binding var todos: [TodoItem]

    // 用於表單綁定的本地狀態變數，初始值來自 originalTask
    @State private var taskTitle: String
    @State private var selectedCategory: TodoItem.TodoCategory
    @State private var selectedPriority: TodoItem.Priority
    @State private var dueDate: Date
    @State private var includeDate: Bool
    @State private var selectedReminder: TodoItem.ReminderOption
    @State private var notes: String
    @State private var showingDeleteAlert = false // 新增狀態變數控制刪除提示

    // 初始化器，用傳入的 originalTask 來設置 @State 變數的初始值
    init(originalTask: TodoItem, todos: Binding<[TodoItem]>) {
        self.originalTask = originalTask
        self._todos = todos // 設置 Binding

        // 初始化 @State 變數
        _taskTitle = State(initialValue: originalTask.title)
        _selectedCategory = State(initialValue: originalTask.category)
        _selectedPriority = State(initialValue: originalTask.priority)
        _dueDate = State(initialValue: originalTask.dueDate ?? Date()) // 如果原始日期為 nil，預設為現在
        _includeDate = State(initialValue: originalTask.dueDate != nil) // 如果原始日期存在，則 Toggle 為 true
        _selectedReminder = State(initialValue: originalTask.reminder)
        _notes = State(initialValue: originalTask.notes ?? "")
    }

    var body: some View {
        NavigationView {
            Form {
                Section("任務資訊") {
                    TextField("任務名稱", text: $taskTitle)
                    Picker("分類", selection: $selectedCategory) {
                        ForEach(TodoItem.TodoCategory.allCases) { cat in
                            Text(cat.rawValue).tag(cat)
                        }
                    }
                    Picker("優先級", selection: $selectedPriority) {
                        ForEach(TodoItem.Priority.allCases) { prio in
                            Text(prio.rawValue).tag(prio)
                        }
                    }
                }

                Section("時間與提醒") {
                    Toggle("設定截止日期", isOn: $includeDate)
                    if includeDate {
                        DatePicker("截止日期", selection: $dueDate, displayedComponents: [.date, .hourAndMinute])
                    }
                    Picker("提醒", selection: $selectedReminder) {
                        ForEach(TodoItem.ReminderOption.allCases, id: \.rawValue) { reminder in
                            Text(reminder.rawValue).tag(reminder)
                        }
                    }
                }

                Section("備註") {
                     TextField("輸入備註 (選填)", text: $notes, axis: .vertical)
                         .lineLimit(3...)
                }

                // --- 新增刪除按鈕 Section ---
                Section {
                    Button(role: .destructive) { 
                        showingDeleteAlert = true 
                    } label: {
                        Text("刪除任務")
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                }
                // --- 刪除按鈕 Section 結束 ---
            }
            .navigationTitle("編輯待辦事項")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("儲存") {
                        saveChanges()
                    }
                    .disabled(taskTitle.isEmpty)
                }
            }
            // --- 新增 .alert 修飾符 ---
            .alert("確認刪除", isPresented: $showingDeleteAlert) {
                Button("確認刪除", role: .destructive) { deleteTask() }
                Button("取消", role: .cancel) { }
            } message: {
                Text("您確定要刪除這個待辦事項嗎？此操作無法復原。")
            }
            // --- .alert 修飾符結束 ---
        }
    }

    private func saveChanges() {
        guard !taskTitle.isEmpty else { return }

        // 在傳入的 todos 陣列中找到原始任務的索引
        if let index = todos.firstIndex(where: { $0.id == originalTask.id }) {
            // 更新該索引位置的 TodoItem
            todos[index].title = taskTitle
            todos[index].category = selectedCategory
            todos[index].priority = selectedPriority
            todos[index].dueDate = includeDate ? dueDate : nil // 如果 Toggle 關閉，則設為 nil
            todos[index].reminder = selectedReminder
            todos[index].notes = notes.isEmpty ? nil : notes
            // isCompleted 狀態通常在 TaskView 的 Row 上直接修改，編輯視圖一般不改它
            // todos[index].isCompleted = originalTask.isCompleted // 保持原樣
        } else {
            print("錯誤：找不到要更新的原始任務！ ID: \(originalTask.id)")
        }

        dismiss() // 關閉編輯視圖
    }

    // --- 新增 deleteTask 函數 ---
    private func deleteTask() {
        if let index = todos.firstIndex(where: { $0.id == originalTask.id }) {
            todos.remove(at: index)
            dismiss() 
        } else {
            print("錯誤：找不到要刪除的原始任務！ ID: \(originalTask.id)")
            dismiss() 
        }
    }
    // --- deleteTask 函數結束 ---
}

// MARK: - Preview (需要提供模擬資料)
struct EditTaskView_Previews: PreviewProvider {
    // 創建一個假的 Binding<[TodoItem]> 供預覽使用
    @State static var previewTodos: [TodoItem] = [
        TodoItem(title: "預覽任務", category: .life, dueDate: Date(), priority: .medium, reminder: .none, estimatedDuration: 60) // Added estimatedDuration
    ]
    // 創建一個假的 originalTask
    static var previewTask = previewTodos[0]

    static var previews: some View {
        EditTaskView(originalTask: previewTask, todos: $previewTodos)
    }
}

// 重要：確保 TodoItem 模型包含以下屬性及 Enum
/* 
struct TodoItem: Identifiable, Codable {
    let id: UUID = UUID()
    var title: String
    var category: TodoCategory // <--- 需要
    var dueDate: Date?        // <--- 改為 Optional
    var priority: Priority
    var reminder: ReminderOption // <--- 需要
    var notes: String?        // <--- 需要，改為 Optional
    var isCompleted: Bool = false

    // ... (Priority enum) ...

    enum TodoCategory: String, CaseIterable, Codable, Identifiable { // <--- 需要
        case study = "課業"
        case life = "生活"
        // Add more if needed
        var id: String { self.rawValue }
    }

    enum ReminderOption: String, CaseIterable, Codable { // <--- 需要
        case none = "無"
        case onTime = "準時提醒"
        case fiveMinBefore = "5 分鐘前"
        case fifteenMinBefore = "15 分鐘前"
        case thirtyMinBefore = "30 分鐘前"
        case oneHourBefore = "1 小時前"
        case oneDayBefore = "1 天前"
    }

    // ... (deadlineString computed property if needed) ...
}
*/ 
