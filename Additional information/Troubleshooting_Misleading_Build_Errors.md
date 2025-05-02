# 記錄：解決誤導性的 Xcode 建置錯誤

## 問題描述

在開發過程中，專案持續出現以下編譯錯誤：

```
/Users/Aibox/ios/NTUB/NTUB/NTUB/Features/Settings/EditProfileView.swift:111:19 Missing arguments for parameters 'category', 'estimatedDuration' in call
/Users/Aibox/ios/NTUB/NTUB/NTUB/Features/Settings/EditProfileView.swift:111:19 Trailing closure passed to parameter of type 'String' that does not accept a closure
```

然而，錯誤訊息指向的檔案 (`EditProfileView.swift`) 和行號 (111行附近，即處理頭像圖片選擇的 `.onChange` 修飾符) 的程式碼，與錯誤內容（缺少 `category`, `estimatedDuration` 參數，通常與 `TodoItem` 初始化相關）**完全不符**。

即使在確認並修正了專案中所有 `TodoItem` 的定義和初始化呼叫（包括 `TaskView.swift` 中的 `AddTaskView` 和 Mock Data，以及 `EditTaskView.swift` 的預覽）後，該錯誤訊息仍然固執地指向 `EditProfileView.swift`。

## 嘗試的解決步驟

1.  **驗證程式碼邏輯**：確認 `EditProfileView.swift` 第 111 行附近的程式碼 (`.onChange` 處理 `PhotosPicker` 結果) 本身語法正確且與 `TodoItem` 無關。
2.  **檢查相關程式碼**：檢查並修正了 `Core/Models/TodoItem.swift` 的定義，確保包含 `estimatedDuration` 屬性。檢查並修正了 `TaskView.swift` 和 `EditTaskView.swift` 中所有 `TodoItem` 的初始化呼叫，確保參數完整且順序正確。
3.  **標準快取清理**：執行 Xcode 的 "Clean Build Folder"。
4.  **深度快取清理**：透過 Xcode 的 "Settings > Locations" 找到並刪除了 `DerivedData` 資料夾內容。
5.  **程式碼隔離（關鍵步驟）**：
    *   註解掉 `EditProfileView.swift` 的整個 `body` 內容 -> 錯誤仍然存在，證明錯誤定位錯誤。
    *   **逐步註解掉 `EditProfileView.swift` 中與頭像選擇功能（使用 `PhotosUI` 和 `PhotosPicker`）相關的所有程式碼。**

## 最終解決方案

在執行完上述步驟 5，將 `EditProfileView.swift` 中頭像功能的程式碼**完全註解掉**並重新建置後，**錯誤消失了**。

隨後，**逐步取消**對頭像功能程式碼的註解（包括 `import`, `@State` 變數, `ZStack` 顯示區塊, `PhotosPicker`, `.onChange` 修飾符），並在**每一步後清理建置資料夾並重新建置**。

最終，所有頭像功能的程式碼都被恢復，且專案可以**正常編譯和運行**，錯誤沒有再出現。

## 結論與反思

這個問題極有可能是由於 **Xcode 的索引損壞、快取殘留或處理特定 SwiftUI 功能（如 `PhotosPicker` 或異步 `Task`）時的內部 Bug** 所導致的。錯誤訊息被錯誤地定位到了與問題根源無關的檔案和行號。

**關鍵解決方法**是透過**程式碼隔離**（暫時註解掉可疑或最近新增的複雜功能區塊）來確認錯誤訊息的定位是否準確，並強制 Xcode 在移除/恢復程式碼的過程中重新評估專案狀態。結合**徹底的快取清理**，最終解決了這個頑固的問題。

未來若遇到類似的、錯誤訊息指向明顯無關程式碼的情況，應優先懷疑 Xcode 環境問題，並嘗試：
1.  深度清理快取 (`DerivedData`)。
2.  透過註解逐步隔離程式碼區塊來找出真正的觸發點。

---
*測試修改：確認 Git 提交流程和 Email 設定。*