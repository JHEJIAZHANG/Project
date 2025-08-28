# Google Classroom 學生資料查詢 API

這個模組提供了兩個新的 API 端點，用於查詢 Google Classroom 中學生的姓名、電子郵件等個人資料。

## API 端點

### 1. 查詢單一學生資料

**端點**: `GET /api/student/profile/`

**用途**: 根據學生的 Google Classroom userId 獲取其個人資料

**參數**:
- `line_user_id`: 老師的 LINE 用戶 ID
- `student_id`: 學生的 Google Classroom userId

**範例請求**:
```bash
GET /api/student/profile/?line_user_id=U1234567890abcdef&student_id=123456789
```

**成功回應** (200):
```json
{
  "success": true,
  "student": {
    "userId": "123456789",
    "name": {
      "givenName": "小明",
      "familyName": "王",
      "fullName": "王小明"
    },
    "emailAddress": "xiaoming.wang@example.com",
    "photoUrl": "https://lh3.googleusercontent.com/...",
    "permissions": [...]
  }
}
```

### 2. 查詢課程中所有學生

**端點**: `GET /api/course/students/`

**用途**: 獲取指定課程中所有學生的資料列表

**參數**:
- `line_user_id`: 老師的 LINE 用戶 ID
- `course_id`: Google Classroom 課程 ID

**範例請求**:
```bash
GET /api/course/students/?line_user_id=U1234567890abcdef&course_id=course_123
```

**成功回應** (200):
```json
{
  "success": true,
  "course_id": "course_123",
  "total_students": 25,
  "students": [
    {
      "userId": "123456789",
      "profileId": "profile_123",
      "name": {
        "givenName": "小明",
        "familyName": "王",
        "fullName": "王小明"
      },
      "emailAddress": "xiaoming.wang@example.com",
      "photoUrl": "https://lh3.googleusercontent.com/...",
      "enrollmentTime": "2024-01-15T08:00:00Z",
      "courseRole": "STUDENT"
    }
  ]
}
```

## 使用場景

### 場景 1: 從作業繳交資料獲取學生姓名

當您從 Google Classroom API 獲取作業繳交資料時，通常只能看到 `userId`，無法直接看到學生姓名：

```json
{
  "userId": "123456789",
  "courseId": "course_123",
  "courseWorkId": "work_456",
  "state": "TURNED_IN"
}
```

要獲取學生姓名，請呼叫：
```bash
GET /api/student/profile/?line_user_id=YOUR_LINE_ID&student_id=123456789
```

### 場景 2: 獲取課程學生名單

要獲取課程中所有學生的完整資料：
```bash
GET /api/course/students/?line_user_id=YOUR_LINE_ID&course_id=course_123
```

## 權限要求

要成功使用這些 API，您的 Google OAuth 應用程式必須包含以下權限範圍：

### 必要權限
- `https://www.googleapis.com/auth/classroom.profile.emails` - 讀取學生個人資料和電子郵件

### 建議權限
- `https://www.googleapis.com/auth/classroom.courses.readonly` - 讀取課程資訊
- `https://www.googleapis.com/auth/classroom.rosters.readonly` - 讀取課程名單

## 錯誤處理

### 權限不足 (403)
```json
{
  "error": "權限不足",
  "message": "無法獲取學生資料，請確認您的應用程式已包含 classroom.profile.emails 權限範圍",
  "details": "需要 scope: https://www.googleapis.com/auth/classroom.profile.emails"
}
```

### 學生不存在 (404)
```json
{
  "error": "學生不存在",
  "message": "找不到指定的學生 ID",
  "student_id": "123456789"
}
```

### 缺少參數 (400)
```json
{
  "error": "缺少必要參數",
  "message": "請提供 line_user_id 和 student_id 參數"
}
```

## 實作細節

### 技術架構
- 使用 Django REST Framework 建立 API 端點
- 整合 Google Classroom API v1
- 自動處理 Google OAuth token 刷新
- 完整的錯誤處理和回應格式化

### 資料流程
1. 接收 API 請求參數
2. 驗證老師的 LINE 用戶 ID 和 Google 憑證
3. 建立 Google Classroom service
4. 呼叫相應的 Google Classroom API
5. 處理回應資料並格式化
6. 返回結構化的 JSON 回應

### 安全性考量
- 驗證老師身份和權限
- 使用 HTTPS 傳輸
- 不記錄敏感資訊
- 適當的錯誤訊息（不洩露內部細節）

## 測試

使用提供的測試文件 `test_student_api.py` 來測試 API 功能：

```bash
cd classroomai/course
python test_student_api.py
```

**注意**: 測試前請替換佔位符為實際的用戶 ID 和課程 ID。

## 常見問題

### Q: 為什麼無法獲取學生電子郵件？
A: 請確認您的 Google OAuth 應用程式包含 `classroom.profile.emails` 權限範圍。

### Q: 可以獲取學生的其他資料嗎？
A: 可以，Google Classroom API 還提供更多學生資料，如照片、權限等。如需擴展功能，可以修改 API 回應格式。

### Q: 如何處理大量學生的課程？
A: 對於學生數量很多的課程，建議實作分頁功能。目前版本會一次性獲取所有學生資料。

### Q: 可以快取學生資料嗎？
A: 可以，建議實作快取機制來減少 API 呼叫次數，提升效能。

## 更新日誌

- **v1.0.0**: 初始版本，支援基本的學生資料查詢功能
- 支援單一學生資料查詢
- 支援課程學生列表查詢
- 完整的錯誤處理和回應格式化
