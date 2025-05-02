# NTUB iOS Project Structure

本文件旨在說明 NTUB iOS 應用程式的專案目錄結構，以便於理解、維護和協作。

專案採用**混合結構**：頂層目錄主要基於**功能 (Features)** 劃分，而共享的核心組件則在 `Core/` 目錄下進一步按**類型 (Types)** 組織。

```
NTUB/NTUB/
├── App/
├── Core/
├── Features/
├── Resources/
└── Preview Content/
```

---

## 目錄詳情

### 1. `App/`

包含應用程式的生命週期管理和主入口點。

*   `NTUBApp.swift`: SwiftUI 應用程式的主要入口點 (`@main` struct)，負責初始化環境（如 `AuthManager`）和設置根視圖（根據登入狀態顯示 `LoginView` 或 `MainTabView`）。

### 2. `Core/`

包含整個應用程式共享的核心組件、基礎程式碼和工具。

*   **`Authentication/`**: 處理使用者身份驗證。
    *   `AuthManager.swift`: `ObservableObject`，管理使用者登入狀態、當前使用者資訊，並處理登入、登出邏輯。
*   **`Constants/`**: (目前為空) 預留用於存放全域常數，如 API 端點 URL、通知名稱、常用的字串鍵等。
*   **`Extensions/`**: Swift 標準類型或外部框架類別的擴展。
    *   `Date+StartOfWeek.swift`: 為 `Date` 添加 `startOfWeek` 計算屬性，用於課表功能。
*   **`Managers/`**: (目前為空) 預留用於存放其他核心管理器，例如網路請求管理器 (`NetworkManager`)、資料持久化管理器等。
*   **`Models/`**: 定義應用程式中使用的資料結構。
    *   `CalendarEvent.swift`: (內容待確認) 可能用於行事曆相關功能。
    *   `Chat.swift`: 定義聊天列表 (`Chat`) 和聊天訊息 (`ChatMessage`) 的資料結構。
    *   `CommunityPost.swift`: 定義社群貼文 (`CommunityPost`) 和貼文話題 (`PostTopic`) 的資料結構。
    *   `DailyStats.swift`: (內容待確認) 可能用於統計相關功能。
    *   `LearningPlan.swift`: (內容待確認) 可能用於學習計畫相關功能。
    *   `MarketplaceItem.swift`: 定義二手市集物品 (`MarketplaceItem`) 和物品分類 (`ItemCategory`) 的資料結構。
    *   `ScheduleCourse.swift`: 定義課表課程 (`ScheduleCourse`) 和星期幾 (`Weekday`) 的資料結構。
    *   `StudyPartner.swift`: (內容待確認) 可能用於學習夥伴相關功能。
    *   `StudyStats.swift`: (內容待確認) 可能用於學習統計。
    *   `Task.swift`: (內容待確認) 可能是舊的任務模型。
    *   `TodoItem.swift`: 定義待辦事項 (`TodoItem`) 的資料結構，包含標題、描述、截止日期、優先級、分類、完成狀態等。
    *   `User.swift`: 定義基本使用者資訊 (`User`) 的資料結構。
    *   `UserProfile.swift`: (內容待確認) 可能用於更詳細的使用者個人資料。
*   **`Utilities/`**: (已移除，內容移至 `Extensions/`) 曾用於存放通用輔助函式或擴展。
*   **`Views/`**: 存放可在多個 Feature 中重複使用的 SwiftUI 視圖組件。
    *   `SectionView.swift`: 一個可重用的視圖，用於在 `PrivacyPolicyView` 中顯示帶有標題的區塊內容。

### 3. `Features/`

包含應用程式的各個主要功能模組，每個子目錄代表一個獨立的功能或畫面流程。

*   **`Chart/`**: 圖表顯示功能。
    *   `ChartView.swift`: (內容待檢視) 顯示圖表的視圖，具體用途和資料來源待確認。
*   **`Community/`**: 社群討論區和聊天功能。
    *   `CommunityView.swift`: 社群主畫面，包含貼文列表 (`List`)、話題篩選 (`TopicPill`)、單一貼文卡片 (`PostCardView`) 和新增貼文表單 (`AddPostView`)。
    *   `ChatView.swift`: 聊天功能主畫面，包含聊天列表 (`List`)、單一聊天列 (`ChatRowView`) 和聊天室佔位視圖 (`ChatRoomView`)。
*   **`Friends/`**: 好友列表功能。
    *   `FriendsView.swift`: (內容待檢視) 好友列表的佔位視圖。
*   **`Home/`**: 應用程式首頁/儀表板。
    *   `HomeView.swift`: 顯示使用者問候、天氣提醒、今日課程區塊 (`CourseCardView`)、待辦事項區塊 (`TodoCardView`)，並提供前往課表頁面的連結。
*   **`Login/`**: 登入和註冊流程。
    *   `LoginView.swift`: 登入畫面 UI，包含學號/密碼輸入、登入按鈕、註冊/忘記密碼連結、開發者跳過登入按鈕。
    *   `RegistrationView.swift`: 註冊畫面 UI，包含帳號、密碼、同意條款等欄位。
    *   `LoginViewModel.swift`: (內容待檢視) 處理登入/註冊相關的業務邏輯和網路請求（預期）。
*   **`MainTab/`**: 應用程式主 Tab 導航容器。
    *   `MainTabView.swift`: 定義 `TabView` 結構，包含首頁、社群、待辦、二手市集、設定等 Tab。
*   **`Marketplace/`**: 二手物品交易市集。
    *   `MarketplaceView.swift`: 包含市集主要畫面 (`MarketplaceListView` - 含搜尋、分類 `CategoryPill`、網格 `ItemCardView`)、物品詳情頁面 (`MarketplaceDetailView` - 含 `SectionHeader`, `DetailRow` 輔助視圖) 和新增/編輯物品表單 (`AddMarketplaceItemView`)。
*   **`Settings/`**: 設定相關功能。
    *   `SettingsView.swift`: 設定主列表畫面，包含各項設定的入口 `NavigationLink`。
    *   `ProfileView.swift`: 使用者個人資料畫面，顯示基本資訊、快速連結 (`QuickLinkButton`)、活動記錄入口。內含 `EditProfileView`, `MyPostsView`, `MyMarketplaceItemsView`, `MyBookmarksView`, `WebView` 等佔位視圖定義。
    *   `PrivacyPolicyView.swift`: 顯示隱私權政策內容。
    *   `AccountSecurityView.swift`: 帳號安全設定的佔位視圖。
    *   `TermsView.swift`: 服務條款的佔位視圖。
    *   `FeedbackView.swift`: 意見回饋的佔位視圖。
    *   `FAQView.swift`: 常見問題的佔位視圖。
    *   `AboutView.swift`: 關於 App 的佔位視圖。
    *   `CommunityPrivacySettingsView.swift`: 社群隱私設定的佔位視圖。
    *   `LinkedAccountsView.swift`: 綁定帳號設定的佔位視圖。
    *   `ChangePasswordView.swift`: 更改密碼畫面的佔位視圖。
*   **`Tasks/`**: 待辦事項管理功能。
    *   `TaskView.swift`: 待辦事項列表畫面，包含分類篩選、按日期分組的列表、單一待辦事項列 (`TodoRowView`)。
    *   `EditTaskView.swift`: (內容待檢視) 編輯待辦事項的表單視圖。
*   **`Timetable/`**: 課程表功能。
    *   `TimetableView.swift`: 顯示週課程表網格、時間軸、課程區塊 (`CourseBlockView`)，提供新增/分享入口。
    *   `AddCourseView.swift`: 新增課程的表單視圖。
    *   `EditCourseView.swift`: 編輯現有課程的表單視圖。
    *   `ShareScheduleView.swift`: 分享課表設定的 UI 視圖。

### 4. `Resources/`

存放非程式碼的資源檔案。

*   **`Assets.xcassets/`**: 應用程式的圖檔、圖示、顏色等資源目錄。
*   **`Supporting Files/`**: 其他輔助檔案，如專案設定檔。
    *   `Info.plist`: 應用程式的屬性列表檔案。
    *   `NTUB.entitlements`: 應用程式的權限設定檔案。

### 5. `Preview Content/`

存放僅供 SwiftUI Previews 使用的資源。

*   **`Preview Assets.xcassets`**: 預覽專用的資源目錄，其內容不會被打包進最終發布的 App。

---

**注意：** 標有 `(內容待確認)` 或 `(內容待檢視)` 的檔案表示其具體實作細節可能需要進一步查看或尚未完全根據需求開發。標有 `(佔位視圖)` 的表示該視圖目前僅為簡單的文字顯示，等待後續開發。 
