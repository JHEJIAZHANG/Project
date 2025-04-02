import SwiftUI

// MARK: - Main Task View
struct TaskView: View {
    @State private var selectedCategory: TodoItem.TodoCategory? = nil // nil for '全部'
    @State private var showingAddTaskSheet = false

    // --- Mock Data ---
    @State private var todos: [TodoItem] = [
        TodoItem(title: "資料庫系統作業", category: .study, dueDate: Calendar.current.date(bySettingHour: 23, minute: 59, second: 0, of: Date()), priority: .high),
        TodoItem(title: "購買計算機概論教科書", category: .life, dueDate: Calendar.current.date(byAdding: .day, value: 2, to: Date()), priority: .medium),
        TodoItem(title: "網頁程式設計小組討論", category: .study, dueDate: Calendar.current.date(byAdding: .day, value: 3, to: Date())?.addingTimeInterval(15*3600+30*60), priority: .low),
        TodoItem(title: "繳交社團費用", category: .life, dueDate: Calendar.current.date(byAdding: .day, value: 5, to: Date()), priority: .medium),
        TodoItem(title: "行動應用開發報告", category: .study, dueDate: Calendar.current.date(byAdding: .day, value: -1, to: Date()), isCompleted: true)
    ]

    // Filtered and Grouped Todos
    var filteredTodos: [TodoItem] {
        todos.filter { todo in
            guard let category = selectedCategory else { return true } // Show all if nil
            return todo.category == category
        }
    }

    var groupedTodos: [String: [TodoItem]] {
        Dictionary(grouping: filteredTodos.filter { !$0.isCompleted }) { todo in
            if let dueDate = todo.dueDate, Calendar.current.isDateInToday(dueDate) {
                return "今日"
            } else if let dueDate = todo.dueDate, Calendar.current.isDateInWeekend(dueDate) { // Example: Future grouping
                return "未來三天" // Simplified, can be more precise
            } else {
                 return "未來" // Catch all for other future dates
            }
        }
    }
    
    var completedTodos: [TodoItem] {
        filteredTodos.filter { $0.isCompleted }
    }
    
    let todoSections = ["今日", "未來三天", "未來"]

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 0) {
                // 1. Top Filter Buttons
                HStack {
                    // Category Filters
                    HStack(spacing: 10) {
                        FilterButton(title: "全部", isSelected: selectedCategory == nil) {
                            selectedCategory = Optional<TodoItem.TodoCategory>.none
                        }
                        FilterButton(title: "課業", isSelected: selectedCategory == .study) {
                            selectedCategory = .study
                        }
                        FilterButton(title: "生活", isSelected: selectedCategory == .life) {
                            selectedCategory = .life
                        }
                    }
                    Spacer()
                    // Add Button
                    Button { showingAddTaskSheet = true } label: {
                        Image(systemName: "plus.circle.fill")
                            .font(.title)
                            .foregroundColor(.blue)
                    }
                }
                .padding()
                .background(Color(.systemBackground)) // Match background
                
                // 2. Todo List
                List {
                    // Upcoming sections
                    ForEach(todoSections, id: \.self) { sectionTitle in
                         if let sectionTodos = groupedTodos[sectionTitle], !sectionTodos.isEmpty {
                            Section(header: Text(sectionTitle).font(.title3).fontWeight(.semibold)) {
                                ForEach(sectionTodos) { todo in
                                     TodoRowView(todo: $todos[getIndex(for: todo)!]) // Use binding
                                }
                            }
                        }
                    }
                    
                    // Completed section
                    if !completedTodos.isEmpty {
                        Section(header: Text("已完成").font(.title3).fontWeight(.semibold)) {
                             ForEach(completedTodos) { todo in
                                 TodoRowView(todo: $todos[getIndex(for: todo)!]) // Use binding
                            }
                        }
                    }
                }
                .listStyle(PlainListStyle()) // Use PlainListStyle to remove default insets/background
            }
            .navigationTitle("待辦事項")
            .navigationBarHidden(true) // Hide default nav bar as we have custom top bar
            .sheet(isPresented: $showingAddTaskSheet) {
                 AddTaskView(todos: $todos) // Pass binding to AddTaskView
            }
        }
    }
    
    // Helper to find the index of a todo item in the original array for binding
    private func getIndex(for todo: TodoItem) -> Int? {
        todos.firstIndex { $0.id == todo.id }
    }
}

// MARK: - Helper Views

// Filter Button
struct FilterButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .padding(.horizontal, 15)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

// Todo Row View
struct TodoRowView: View {
    @Binding var todo: TodoItem

    var body: some View {
        HStack(spacing: 15) {
            // Checkbox
            Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                .foregroundColor(todo.isCompleted ? .gray : todo.priority.color)
                .font(.title2)
                .onTapGesture {
                    todo.isCompleted.toggle()
                }

            // Title and Deadline
            VStack(alignment: .leading) {
                Text(todo.title)
                    .font(.headline)
                    .strikethrough(todo.isCompleted, color: .gray)
                    .foregroundColor(todo.isCompleted ? .gray : .primary)
                if let dueDate = todo.dueDate {
                     Text(todo.deadlineString)
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
            }

            Spacer()

            // Priority Tag
            Text(todo.priority.rawValue)
                .font(.caption)
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(todo.priority.color.opacity(0.2))
                .foregroundColor(todo.priority.color)
                .cornerRadius(10)
        }
        .padding(.vertical, 8)
        .opacity(todo.isCompleted ? 0.6 : 1.0) // Dim completed items
    }
}

// MARK: - Add Task View (Placeholder for now, needs implementation)
struct AddTaskView: View {
    @Environment(\.presentationMode) var presentationMode
    @Binding var todos: [TodoItem] // Receive the binding
    
    // Add State variables for the form fields
    @State private var taskTitle: String = ""
    @State private var selectedCategory: TodoItem.TodoCategory = .study
    @State private var selectedPriority: TodoItem.Priority = .medium
    @State private var dueDate: Date = Date()
    @State private var includeDate: Bool = false // Toggle for setting due date
    @State private var selectedReminder: TodoItem.ReminderOption = .none
    @State private var notes: String = ""

    var body: some View {
         NavigationView {
             // TODO: Implement the form based on prototype
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
                 
                 Section {
                     Button("添加任務") {
                         addTask()
                     }
                 }
             }
             .navigationTitle("添加待辦事項")
             .navigationBarItems(
                 leading: Button("取消") {
                     presentationMode.wrappedValue.dismiss()
                 }
             )
         }
    }
    
    private func addTask() {
        guard !taskTitle.isEmpty else { /* show alert */ return }
        
        let newTodo = TodoItem(
            title: taskTitle,
            category: selectedCategory,
            dueDate: includeDate ? dueDate : nil,
            priority: selectedPriority,
            reminder: selectedReminder,
            notes: notes.isEmpty ? nil : notes
        )
        todos.append(newTodo)
        presentationMode.wrappedValue.dismiss()
    }
}


// MARK: - Preview
#Preview {
    TaskView()
} 