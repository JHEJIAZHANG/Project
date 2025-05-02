# NTUB 校園生活 App 開發狀態追蹤 (佔位符與未完成部分)

## 一、需要後端連接 (用於獲取/提交數據)

以下部分目前使用假資料或僅有 UI 骨架，最終需要與後端 API 對接才能實現完整功能：

*   **用戶認證與資料**
    *   `LoginView`:
        *   忘記密碼流程 (觸發後端重設流程)。
    *   `RegistrationView`:
        *   提交註冊資料 (`/api/register/`)。
        *   *(待辦)* 需要在 UI 新增 Email 輸入欄位以符合後端要求。
    *   `ProfileView`:
        *   獲取用戶個人資料 (姓名、系級、頭像等)。
        *   更新用戶個人資料。
    *   `ChangePasswordView`:
        *   提交新密碼以更改用戶密碼。
    *   `LinkedAccountsView`:
        *   獲取已綁定的第三方帳號狀態。
        *   處理綁定/解綁流程。
    *   `SettingsView` - 通知開關:
        *   向後端註冊/更新裝置的推播 token。
        *   向後端更新用戶的通知偏好設定。

*   **課表 (`Timetable`)**
    *   `TimetableView`:
        *   獲取用戶的個人課表資料。
        *   搜尋課程功能。
    *   `AddCourseView`:
        *   儲存新增的課程到用戶課表。
    *   `ShareScheduleView`:
        *   生成/獲取課表共享連結或代碼。
        *   (可能) 獲取他人共享給自己的課表。

*   **待辦事項 (`Task`)**
    *   `TaskView`:
        *   獲取用戶的待辦事項列表。

*   **二手市集 (`Marketplace`)**
    *   `MarketplaceView`:
        *   獲取商品列表。
        *   按分類篩選商品。
        *   搜尋商品。
    *   `AddMarketplaceItemView`:
        *   儲存新增的商品資訊。
        *   上傳商品圖片 (需要後端儲存支持)。
    *   `MarketplaceDetailView`:
        *   獲取特定商品的詳細資訊。
        *   觸發 "聯絡賣家" (可能需要後端創建聊天或發送通知)。

*   **社群 (`Community`)**
    *   `CommunityView`:
        *   獲取社群貼文列表。
        *   按話題篩選貼文。
        *   搜尋貼文。
        *   提交按讚/取消讚。
        *   (未來) 提交留言。
    *   `AddPostView`:
        *   儲存新增的貼文 (包含匿名狀態、話題)。
        *   (可能) 獲取可選的話題列表。

*   **聊天 (`Chat`)**
    *   `ChatListView`:
        *   獲取用戶的聊天對象列表。
        *   搜尋聊天列表。
    *   `ChatView`:
        *   獲取特定聊天的歷史訊息。
        *   透過 WebSocket 或其他方式即時接收新訊息。
        *   發送訊息。

*   **首頁 (`HomeView`)**
    *   獲取用戶今日的課程預覽。
    *   獲取用戶待辦事項預覽。

## 二、主要為本地內容 / 客戶端邏輯 (初期無需後端)

以下部分目前是佔位符或只需要在客戶端完成 UI 或基本邏輯，部分功能的最終動作 (如提交) 可能仍需後端。

*   **`SettingsView` 及其子頁面**
    *   `CommunityPrivacySettingsView`: *(連結被註解)* 若啟用，需建立佔位符頁面 (本地靜態內容)。
    *   `AboutView`: 需填充 App 版本、開發資訊等 (本地靜態內容)。
    *   `FAQView`: 需填充常見問題與解答 (本地靜態內容)。
    *   `FeedbackView`: 需建立意見回饋表單 UI (本地 UI)；*提交意見需要後端*。
    *   `TermsView`: 需填充服務條款 (本地靜態內容)。
    *   `PrivacyPolicyView`: 已填充基本範本 (本地靜態內容)，待最終審閱。
    *   `AccountSecurityView`: 需建立佔位符頁面 (本地靜態內容)；*具體功能 (如 2FA) 可能需後端*。
    *   佈景主題切換: 功能已基本實現 (本地邏輯)。

*   **`RegistrationView`**
    *   "服務條款及隱私權政策" 複選框: 需連結至 `TermsView` 和 `PrivacyPolicyView` (本地導航)。

*   **`HomeView`**
    *   天氣提醒: *(暫定)* 可直接從客戶端調用第三方天氣 API (無需自建後端)。

*   **`TimetableView`**
    *   "本週" 按鈕: 跳轉至當前週的邏輯 (本地邏輯)。

*   **`TaskView`**
    *   分類篩選按鈕: 對已獲取的數據進行客戶端篩選 (本地邏輯)。

*   **`ChatListView`**
    *   點擊列表項目導航至 `ChatView`: (本地導航)。 