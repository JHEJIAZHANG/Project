# 批量作業提交狀態查詢 API

## 概述

`get_submissions_status` API 現在支援批量查詢多課程多作業的提交狀態，並自動為教師發送 Flex Message 統計圖表。

## 支援的查詢模式

### 1. 批量查詢模式 - 方法一：使用 course_coursework_pairs

```json
{
  "line_user_id": "U1234567890abcdef",
  "course_coursework_pairs": [
    {
      "course_id": "course_id_1",
      "coursework_id": "coursework_id_1"
    },
    {
      "course_id": "course_id_2", 
      "coursework_id": "coursework_id_2"
    },
    {
      "course_id": "course_id_3",
      "coursework_id": "coursework_id_3"
    }
  ]
}
```

### 2. 批量查詢模式 - 方法二：使用 course_ids + coursework_ids

```json
{
  "line_user_id": "U1234567890abcdef",
  "course_ids": ["course_id_1", "course_id_2", "course_id_3"],
  "coursework_ids": ["coursework_id_1", "coursework_id_2", "coursework_id_3"]
}
```

### 3. 單一課程單作業查詢（使用批量格式）

```json
{
  "line_user_id": "U1234567890abcdef",
  "course_coursework_pairs": [
    {
      "course_id": "course_id_1",
      "coursework_id": "coursework_id_1"
    }
  ]
}
```

## 回傳格式

### 批量查詢模式回傳

```json
{
  "query_mode": "batch",
  "total_queries": 3,
  "successful_queries": 2,
  "failed_queries": 1,
  "teacher_queries": 1,
  "student_queries": 1,
  "flex_messages_sent": 1,
  "results": [
    {
      "course_id": "course_id_1",
      "coursework_id": "coursework_id_1",
      "course_name": "課程1",
      "homework_title": "作業1",
      "role": "teacher",
      "statistics": {
        "total_students": 30,
        "submitted": 25,
        "unsubmitted": 5,
        "completion_rate": 83.3,
        "status_counts": {
          "TURNED_IN": 20,
          "RETURNED": 5,
          "CREATED": 5
        }
      },
      "unsubmitted_students": [
        {
          "name": "學生姓名",
          "userId": "student_id",
          "emailAddress": "student@example.com"
        }
      ],
      "flex_message_sent": true
    },
    {
      "course_id": "course_id_2",
      "coursework_id": "coursework_id_2",
      "course_name": "課程2",
      "homework_title": "作業2",
      "role": "student",
      "status": "CREATED",
      "status_text": "❌ 未繳交",
      "is_late": false,
      "update_time": "無更新時間"
    },
    {
      "course_id": "course_id_3",
      "coursework_id": "coursework_id_3",
      "error": "查詢失敗",
      "message": "課程不存在或無權限訪問"
    }
  ]
}
```

## Flex Message 功能

### 自動發送機制
- **教師查詢**：自動發送統計圖表到 LINE
- **學生查詢**：不發送 Flex Message
- **批量查詢**：為每個教師查詢結果發送獨立的 Flex Message

### Flex Message 內容
- 課程名稱和作業標題
- 繳交統計數據（總人數、已繳交、未繳交、繳交率）
- 缺交學生名單（保護個資）
- 狀態分布圖表

### 發送狀態追蹤
- `flex_messages_sent`：成功發送的 Flex Message 數量
- `flex_message_sent`：個別查詢的發送狀態
- `flex_message_error`：發送失敗的錯誤訊息

## 使用場景

### 1. 教師批量查詢多課程作業狀態
- 一次查詢多個課程的作業繳交情況
- 自動收到每個作業的統計圖表
- 快速了解整體教學進度

### 2. 教師查詢單一課程多作業
- 查看同一課程的所有作業狀態
- 收到該課程所有作業的統計圖表
- 節省多次查詢的時間

### 3. 學生查看多課程作業狀態
- 一次查看所有課程的作業繳交狀態
- 快速識別需要繳交的作業
- 提高學習效率

### 4. 系統整合
- 支援 n8n 等自動化工具
- 批量資料同步
- 報表生成

## 注意事項

1. **統一查詢格式**：所有查詢都使用批量格式，包括單一課程單作業
2. **角色辨識**：系統會自動識別每個課程中用戶的角色（教師/學生）
3. **錯誤處理**：批量查詢中個別查詢失敗不會影響其他查詢
4. **資料暫存**：教師查詢會使用資料庫暫存機制，提高效能並保護學生個資
5. **Flex Message**：教師查詢會自動發送統計圖表到 LINE
6. **API 限制**：Google Classroom API 有呼叫頻率限制，建議合理控制批量查詢數量

## 效能優化

- 使用資料庫暫存減少 Google API 呼叫
- 批量處理減少網路延遲
- 智能錯誤處理，失敗的查詢不影響成功的查詢
- 支援高達 200 個學生的作業狀態查詢
- 並行發送 Flex Message，提高響應速度

## 安全性

- 學生個資不會透過 API 回傳
- 教師身份驗證確保資料安全
- 資料庫暫存機制保護隱私
- 支援 LINE 用戶身份驗證
- Flex Message 中的學生資料經過脫敏處理

## 錯誤處理

### 常見錯誤類型
1. **參數驗證錯誤**：缺少必要參數或格式不正確
2. **權限錯誤**：用戶無權限訪問課程
3. **課程不存在**：課程 ID 無效
4. **Flex Message 發送失敗**：LINE Bot 設定問題

### 錯誤回傳格式
```json
{
  "error": "查詢作業狀態失敗",
  "message": "錯誤描述",
  "details": "詳細錯誤訊息"
}
```

## 最佳實踐

### 1. 查詢數量控制
- 建議單次查詢不超過 20 個課程作業組合
- 大量查詢建議分批處理

### 2. 錯誤處理
- 檢查 `failed_queries` 數量
- 查看個別結果的錯誤訊息
- 重試失敗的查詢

### 3. Flex Message 監控
- 檢查 `flex_messages_sent` 數量
- 確認 LINE Bot 設定正確
- 監控發送失敗的案例
