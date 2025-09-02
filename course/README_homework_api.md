# 作業管理 API 說明

## 🎯 功能概述

作業管理 API 提供了完整的作業 CRUD 操作，包括創建、查詢、更新和刪除作業。現在支援多課程ID查詢，可以一次查詢多個課程的作業。

## 🔄 API 端點

### 1. 創建作業 (支援多課程)

```
POST /api/homeworks/
```

**請求參數：**
```json
{
  "line_user_id": "U1234567890abcdef",
  "course_id": "course1,course2,course3",  // 支援多個課程ID，用逗號分隔
  "title": "作業標題",
  "description": "作業說明",  // 可選
  "due": "2024-12-31"  // 到期日期
}
```

**回應格式：**
```json
{
  "message": "作業創建成功",
  "total_courses": 3,
  "results": [
    {
      "course_id": "course1",
      "course_name": "課程1",
      "homework_id": "hw1",
      "status": "success"
    }
  ],
  "errors": []  // 如果有錯誤會記錄在這裡
}
```

### 2. 查詢作業 (支援多課程)

```
GET /api/get-homeworks/?course_id=course1,course2&line_user_id=U1234567890abcdef
```

**查詢參數：**
- `course_id`: 課程ID，支援多個ID用逗號分隔
- `line_user_id`: LINE 用戶ID

**回應格式：**
```json
{
  "total_courses": 2,
  "total_homeworks": 5,
  "course_summaries": [
    {
      "course_id": "course1",
      "course_name": "Python程式設計",
      "course_section": "1131班",
      "total_homeworks": 3,
      "homeworks": [
        {
          "id": "hw1",
          "title": "第一次作業",
          "description": "Python基礎語法練習",
          "state": "PUBLISHED",
          "workType": "ASSIGNMENT",
          "dueDate": "2024-12-31 23:59",
          "creationTime": "2024-01-01T00:00:00Z",
          "updateTime": "2024-01-01T00:00:00Z",
          "maxPoints": 100,
          "assigneeMode": "ALL_STUDENTS",
          "course_id": "course1"
        }
      ]
    },
    {
      "course_id": "course2",
      "course_name": "資料結構",
      "course_section": "1131班",
      "total_homeworks": 2,
      "homeworks": [...]
    }
  ],
  "all_homeworks": [...]  // 所有作業的平鋪列表
}
```

### 3. 更新作業

```
PATCH /api/homeworks/update/
```

**請求參數：**
```json
{
  "line_user_id": "U1234567890abcdef",
  "course_id": "course1",
  "homework_id": "hw1",
  "title": "更新後的標題",
  "description": "更新後的說明",
  "due": "2024-12-30"
}
```

### 4. 刪除作業

```
DELETE /api/delete_homework/
```

**請求參數：**
```json
{
  "line_user_id": "U1234567890abcdef",
  "course_id": "course1",
  "homework_id": "hw1"
}
```

## ✨ 新功能特色

### 多課程ID支援

1. **創建作業**: 可以同時在多個課程中創建相同的作業
2. **查詢作業**: 可以一次查詢多個課程的作業，提高效率
3. **錯誤處理**: 如果某個課程處理失敗，不會影響其他課程的處理

### 使用範例

#### 查詢多個課程的作業

```bash
# 查詢兩個課程的作業
GET /api/get-homeworks/?course_id=course1,course2&line_user_id=U1234567890abcdef

# 查詢三個課程的作業
GET /api/get-homeworks/?course_id=course1,course2,course3&line_user_id=U1234567890abcdef
```

#### 創建多課程作業

```bash
# 在兩個課程中創建相同的作業
POST /api/homeworks/
{
  "line_user_id": "U1234567890abcdef",
  "course_id": "course1,course2",
  "title": "期末作業",
  "description": "請完成期末專案",
  "due": "2024-12-31"
}
```

## 🔧 技術實現

### 課程ID分割

```python
# 分割課程ID（支援多個課程）
course_ids = [cid.strip() for cid in course_id_param.split(",") if cid.strip()]
```

### 錯誤處理策略

- 如果某個課程不存在或無權限訪問，會記錄錯誤但繼續處理其他課程
- 所有錯誤都會記錄在 `course_summaries` 中，不會中斷整個請求
- 權限不足等嚴重錯誤會立即返回，不會繼續處理

### 回應數據結構

- `course_summaries`: 每個課程的作業摘要，包含錯誤信息
- `all_homeworks`: 所有作業的平鋪列表，便於前端處理
- `total_courses`: 請求的課程總數
- `total_homeworks`: 所有課程的作業總數

## 📱 前端整合建議

### 1. 批量查詢

```javascript
// 查詢多個課程的作業
const courseIds = ['course1', 'course2', 'course3'];
const response = await fetch(`/api/get-homeworks/?course_id=${courseIds.join(',')}&line_user_id=${userId}`);
const data = await response.json();

// 顯示每個課程的作業
data.course_summaries.forEach(course => {
  if (course.error) {
    console.log(`課程 ${course.course_id} 錯誤: ${course.error}`);
  } else {
    console.log(`課程 ${course.course_name}: ${course.total_homeworks} 個作業`);
  }
});
```

### 2. 錯誤處理

```javascript
// 檢查是否有課程處理失敗
const failedCourses = data.course_summaries.filter(course => course.error);
if (failedCourses.length > 0) {
  console.warn('以下課程處理失敗:', failedCourses);
}
```

### 3. 數據展示

```javascript
// 顯示所有作業的平鋪列表
data.all_homeworks.forEach(homework => {
  console.log(`${homework.title} (${homework.course_id})`);
});
```

## 🚀 性能優化

1. **並行處理**: 多個課程的作業查詢可以並行執行
2. **錯誤隔離**: 單個課程的錯誤不會影響其他課程
3. **數據聚合**: 提供多種數據視角，滿足不同的前端需求

## 📝 注意事項

1. **課程ID格式**: 多個課程ID必須用逗號分隔，不能有空格
2. **權限檢查**: 每個課程都會進行權限驗證
3. **錯誤處理**: 建議前端檢查 `course_summaries` 中的錯誤信息
4. **數據一致性**: 如果某個課程處理失敗，該課程的作業數據可能不完整
