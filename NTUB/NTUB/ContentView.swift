//
//  ContentView.swift
//  NTUB
//
//  Created by Aibox on 2025/3/31.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("首頁", systemImage: "house.fill")
                }
            
            TaskView()
                .tabItem {
                    Label("任務", systemImage: "list.bullet.clipboard.fill")
                }
            
            ChartView()
                .tabItem {
                    Label("圖表", systemImage: "chart.bar.xaxis")
                }
            
            SocialView()
                .tabItem {
                    Label("社群", systemImage: "person.2.fill")
                }
            
            SettingsView()
                .tabItem {
                    Label("設定", systemImage: "gearshape.fill")
                }
        }
    }
}

#Preview {
    ContentView()
}
