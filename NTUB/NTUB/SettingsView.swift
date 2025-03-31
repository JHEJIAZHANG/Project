import SwiftUI

struct SettingsView: View {
    @State private var notificationsEnabled = true
    @State private var soundEnabled = true
    @State private var darkModeEnabled = false
    @State private var focusTime: TimeInterval = 25 * 60 // 25分鐘
    @State private var breakTime: TimeInterval = 5 * 60 // 5分鐘
    @State private var showingProfile = false
    @State private var showingPrivacy = false
    @State private var showingAbout = false
    
    var body: some View {
        NavigationView {
            Form {
                // 個人資料區段
                Section {
                    Button(action: { showingProfile = true }) {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .resizable()
                                .frame(width: 50, height: 50)
                                .foregroundColor(.gray)
                            
                            VStack(alignment: .leading) {
                                Text("用戶名稱")
                                    .font(.headline)
                                Text("查看和編輯個人資料")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            .padding(.leading, 8)
                        }
                    }
                }
                
                // 專注設定
                Section(header: Text("專注設定")) {
                    Stepper(
                        "專注時長：\(Int(focusTime / 60))分鐘",
                        value: $focusTime,
                        in: 5 * 60...60 * 60,
                        step: 5 * 60
                    )
                    
                    Stepper(
                        "休息時長：\(Int(breakTime / 60))分鐘",
                        value: $breakTime,
                        in: 1 * 60...30 * 60,
                        step: 1 * 60
                    )
                }
                
                // 通知設定
                Section(header: Text("通知設定")) {
                    Toggle("允許通知", isOn: $notificationsEnabled)
                    Toggle("音效", isOn: $soundEnabled)
                }
                
                // 外觀設定
                Section(header: Text("外觀設定")) {
                    Toggle("深色模式", isOn: $darkModeEnabled)
                }
                
                // 其他設定
                Section(header: Text("其他")) {
                    Button(action: { showingPrivacy = true }) {
                        SettingRow(
                            icon: "lock.fill",
                            title: "隱私權政策",
                            color: .blue
                        )
                    }
                    
                    Button(action: { showingAbout = true }) {
                        SettingRow(
                            icon: "info.circle.fill",
                            title: "關於",
                            color: .blue
                        )
                    }
                    
                    Button(action: {
                        // TODO: 實作登出功能
                    }) {
                        SettingRow(
                            icon: "arrow.right.square.fill",
                            title: "登出",
                            color: .red
                        )
                    }
                }
            }
            .navigationTitle("設定")
            .sheet(isPresented: $showingProfile) {
                NavigationView {
                    Text("個人資料編輯頁面")
                        .navigationTitle("個人資料")
                        .navigationBarItems(trailing: Button("完成") {
                            showingProfile = false
                        })
                }
            }
            .sheet(isPresented: $showingPrivacy) {
                NavigationView {
                    Text("隱私權政策內容")
                        .navigationTitle("隱私權政策")
                        .navigationBarItems(trailing: Button("關閉") {
                            showingPrivacy = false
                        })
                }
            }
            .sheet(isPresented: $showingAbout) {
                NavigationView {
                    Text("關於應用程式的資訊")
                        .navigationTitle("關於")
                        .navigationBarItems(trailing: Button("關閉") {
                            showingAbout = false
                        })
                }
            }
        }
    }
}

struct SettingRow: View {
    let icon: String
    let title: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
            Text(title)
        }
    }
}

#Preview {
    SettingsView()
} 