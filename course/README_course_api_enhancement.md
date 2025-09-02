# get_courses API 增強功能說明

## 🎯 功能概述

`get_courses` API 現在已經增強，能夠為每個課程提供詳細的老師資訊和用戶角色標識。這讓前端應用程式能夠清楚地知道：

1. **每個課程的老師是誰**（姓名、Email、Google ID）
2. **當前用戶在每個課程中的角色**（老師或學生）

## 🔄 API 端點

```
GET /api/courses/?line_user_id=xxx
```

## 📊 回應資料結構

### 基本回應格式

```json
{
  "line_user_id": "U1234567890abcdef",
  "user_email": "user@example.com",
  "user_role": "teacher",
  "total_courses": 3,
  "courses": [...]
}
```

### 課程資料結構

每個課程現在包含以下新增欄位：

```json
{
  "id": "711324156828",
  "name": "1131Python程式設計",
  "section": "",
  "description": "",
  "ownerId": "108749137057068937391",
  "enrollmentCode": "",
  "courseState": "ACTIVE",
  "creationTime": "2024-09-06T11:53:37.403Z",
  "updateTime": "2024-09-06T11:53:37.403Z",
  "teacherFolder": {},
  "courseGroup": {},
  "guardiansEnabled": false,
  "calendarId": "c_classroom6ea5c11b@group.calendar.google.com",
  "gradebookSettings": {
    "calculationType": "TOTAL_POINTS",
    "displaySetting": "HIDE_OVERALL_GRADE"
  },
  "teacher": {
    "id": "108749137057068937391",
    "name": "王小明",
    "email": "teacher@example.com"
  },
  "userRole": "老師"
}
```

## 🔍 新增欄位說明

### 1. `teacher` 物件
- **`id`**: 老師的 Google 用戶 ID（與 `ownerId` 相同）
- **`name`**: 老師的完整姓名
- **`email`**: 老師的電子郵件地址

### 2. `userRole` 欄位
- **`"老師"`**: 當前用戶是該課程的老師
- **`"學生"`**: 當前用戶是該課程的學生
- **`"未知"`**: 無法確定用戶角色（通常是因為無法獲取老師資料）

## ⚙️ 實作邏輯

### 角色判斷流程

1. **獲取課程擁有者 ID**: 從課程資料中提取 `ownerId`
2. **查詢老師資料**: 使用 `userProfiles.get()` API 獲取老師的詳細資訊
3. **比較 Email**: 將當前用戶的 email 與老師的 email 進行比較
4. **設定角色**: 
   - 如果 email 相同 → `userRole = "老師"`
   - 如果 email 不同 → `userRole = "學生"`
   - 如果無法獲取老師資料 → `userRole = "未知"`

### 錯誤處理

- 如果某個課程無法獲取老師資料，不會影響其他課程的處理
- 所有錯誤都會記錄到日誌中，便於除錯
- 失敗的課程會設定 `teacher = null` 和 `userRole = "未知"`

## 📝 使用範例

### 前端應用程式

```javascript
// 呼叫 API
fetch('/api/courses/?line_user_id=U1234567890abcdef')
  .then(response => response.json())
  .then(data => {
    console.log(`用戶在 ${data.total_courses} 門課中的角色：`);
    
    data.courses.forEach(course => {
      console.log(`課程: ${course.name}`);
      console.log(`老師: ${course.teacher?.name || '未知'}`);
      console.log(`用戶角色: ${course.userRole}`);
      
      // 根據角色顯示不同的 UI
      if (course.userRole === '老師') {
        showTeacherControls(course);
      } else {
        showStudentControls(course);
      }
    });
  });
```

### 角色特定功能

```javascript
function showTeacherControls(course) {
  // 顯示老師專用功能
  // - 建立作業
  // - 管理學生
  // - 查看統計
}

function showStudentControls(course) {
  // 顯示學生專用功能
  // - 繳交作業
  // - 查看成績
  // - 參與討論
}
```

## 🚀 效能考量

### API 呼叫次數
- **之前**: 1 次 API 呼叫（獲取課程列表）
- **現在**: 1 + N 次 API 呼叫（課程列表 + 每個課程的老師資料）

### 優化建議
1. **快取機制**: 考慮實作老師資料的快取，避免重複查詢
2. **批次查詢**: 如果 Google Classroom API 支援，可以考慮批次查詢老師資料
3. **延遲載入**: 可以考慮先顯示課程列表，再非同步載入老師資料

## 🔒 隱私與安全

- 老師的 email 地址會暴露給所有課程參與者
- 這是 Google Classroom 的標準行為，與原始 API 一致
- 如果需要隱藏 email，可以在回應中過濾掉該欄位

## 🧪 測試

使用提供的測試腳本 `test_course_api.py` 來驗證功能：

```bash
cd classroomai
python test_course_api.py
```

## 📚 相關 API

- `GET /api/student/profile/` - 查詢學生個人資料
- `GET /api/course/students/` - 獲取課程中的學生列表
- `GET /api/profile/<line_user_id>/` - 獲取用戶個人資料

## 🔄 版本相容性

這個增強功能向後相容，不會影響現有的 API 使用方式。新增的欄位是可選的，如果前端不需要這些資訊，可以忽略這些欄位。

