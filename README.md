# NTUB 校園生活 App (iOS)

## 專案目標

此專案旨在根據提供的 HTML 原型圖 (`prototype/showcase.html`)，使用 Swift 和 SwiftUI 技術建立「NTUB 校園生活」iOS 應用程式的前端部分。

## 技術棧

*   **語言**: Swift
*   **UI 框架**: SwiftUI

## 目前已完成功能 (UI 骨架)

以下是基於原型圖初步完成的 UI 功能模組，目前主要使用靜態假資料：

*   **登入 / 註冊**:
    *   學號與密碼登入表單。
    *   Google 帳號登入按鈕 (包含呼叫 Google Sign-In SDK 的基本流程)。
    *   Facebook 帳號登入按鈕 (僅 UI)。
    *   註冊表單 (姓名、學號、信箱、密碼、同意條款)。
    *   忘記密碼連結 (僅 UI)。
    *   開發者模式：提供一個按鈕可跳過登入直接進入主畫面以方便 UI 檢視。
*   **主 Tab 導航**:
    *   底部 Tab Bar 包含五個主要功能分頁：首頁、課表、待辦、二手市集、社群。
*   **首頁儀表板 (`HomeView`)**:
    *   顯示使用者問候語及頭像佔位符。
    *   顯示天氣提醒區塊。
    *   顯示「今日課程」列表卡片。
    *   顯示「待辦事項」列表卡片 (僅顯示部分項目)。
*   **課表 (`TimetableView`)**:
    *   週視圖佈局，包含時間軸 (08:00 - 17:00) 和星期標頭 (一至五)。
    *   根據假資料顯示課程方塊。
    *   頂部操作欄包含「本週」按鈕、搜尋按鈕、共享按鈕、新增按鈕。
    *   **新增課程表單 (`AddCourseView`)**: 以 Sheet 彈出，包含名稱、教師、教室、星期、時間、顏色、備註欄位。
    *   **共享課表頁面 (`ShareScheduleView`)**: 以 Sheet 彈出，包含共享開關、連結、好友列表骨架。
*   **待辦事項 (`TaskView`)**:
    *   頂部提供「全部」、「課業」、「生活」分類篩選按鈕。
    *   右上角有新增按鈕。
    *   列表按「今日」、「未來」、「已完成」分組顯示。
    *   待辦事項行 (`TodoRowView`) 包含勾選框、標題、截止日期、優先級標籤。
    *   **新增待辦表單 (`AddTaskView`)**: 以 Sheet 彈出，包含名稱、分類、優先級、截止日期/時間、提醒、備註欄位。
*   **二手市集 (`MarketplaceView`)**:
    *   **列表頁面 (`MarketplaceListView`)**: 包含搜尋欄、分類標籤、物品網格顯示 (圖片佔位符、名稱、價格、狀態)、新增按鈕。
    *   **物品詳情頁面 (`MarketplaceDetailView`)**: 顯示物品圖片佔位符、名稱、價格、賣家資訊、物品詳情、描述、收藏按鈕、聯絡賣家按鈕。
    *   **發布物品表單 (`AddMarketplaceItemView`)**: 以 Sheet 彈出，包含圖片上傳區佔位符、名稱、類別、價格、狀態、地點、描述欄位。
*   **社群 (`CommunityView`)**:
    *   **貼文列表 (`CommunityView`)**: 包含搜尋欄、話題分類標籤、貼文卡片列表 (`PostCardView` - 顯示作者、時間、話題、內容、圖片佔位符、互動按鈕)、新增貼文按鈕。
    *   **發布貼文表單 (`AddPostView`)**: 以 Sheet 彈出，包含實名/匿名切換、文字輸入、添加照片按鈕、話題選擇。
    *   **聊天列表 (`ChatListView` in `ChatView.swift`)**: 包含搜尋欄、聊天列表骨架 (`ChatRowView` - 顯示頭像佔位符、名稱、最新訊息、時間、未讀數)。

## 專案結構

```
NTUB/
├── NTUB.xcodeproj
├── NTUB/
│   ├── Models/            # 資料模型 (目前只有 TodoItem.swift)
│   │   └── TodoItem.swift
│   ├── Views/             # SwiftUI 視圖 (建議將所有 .swift 視圖檔案移至此處)
│   │   ├── LoginView.swift
│   │   ├── RegistrationView.swift
│   │   ├── HomeView.swift
│   │   ├── TimetableView.swift
│   │   ├── ShareScheduleView.swift
│   │   ├── TaskView.swift
│   │   ├── MarketplaceView.swift
│   │   ├── CommunityView.swift
│   │   └── ChatView.swift
│   │   // ... (其他輔助 View 或未使用 View: FriendsView, SettingsView, ChartView)
│   ├── Assets.xcassets    # 圖片及顏色資源
│   ├── NTUBApp.swift      # App 入口點
│   ├── Info.plist
│   └── ...                # 其他 Xcode 專案檔案
└── prototype/
    └── showcase.html      # HTML 原型
```

*建議後續將所有 SwiftUI 視圖檔案歸類到 `Views/` 子目錄下，並將所有資料模型檔案歸類到 `Models/` 目錄下，以保持結構清晰。*

## 待辦事項 / 未來工作

*   [ ] **UI 細化**: 根據原型調整各頁面的視覺細節、間距、顏色、字體。
*   [ ] **圖片處理**: 實現圖片選擇器 (相簿/相機) 及上傳功能 (二手市集、社群貼文)。
*   [ ] **後端整合**: 設計並連接後端 API，替換假資料，實現數據持久化和用戶驗證。
*   [ ] **聊天功能**: 實現 `ChatRoomView` 的訊息顯示和輸入功能 (需後端支持)。
*   [ ] **共享功能**: 完善課表共享邏輯 (需後端支持)。
*   [ ] **使用者狀態**: 管理登入後的使用者資訊。
*   [ ] **錯誤處理**: 為網路請求、表單驗證等添加更完善的錯誤提示。
*   [ ] **程式碼整理**: 
    *   將所有資料模型移至 `Models/` 目錄。
    *   將所有視圖檔案移至 `Views/` 目錄。
    *   評估並移除未使用的檔案 (`FriendsView.swift`, `SettingsView.swift`, `ChartView.swift`)。
*   [ ] **發布準備**: 移除或使用 `#if DEBUG` 包裹開發者模式跳過登入功能。
*   [ ] **測試**: 添加單元測試和 UI 測試。 