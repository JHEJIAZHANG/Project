# API V2 文檔

這是ClassroomAI的API V2版本，提供了課程、作業、考試和筆記的管理功能，支持非Google Classroom課程。

## 認證方式

支持兩種認證方式：

1. **Session認證**：適用於網頁應用，通過Django的session機制進行認證。
2. **LINE認證**：適用於LINE Bot應用，通過LINE用戶ID進行認證。
   - 可以通過HTTP頭部 `X-Line-User-ID` 提供LINE用戶ID
   - 或者通過查詢參數 `line_user_id` 提供LINE用戶ID

## API端點

### 課程 API

- **GET /api/v2/courses/** - 獲取課程列表
- **POST /api/v2/courses/** - 創建新課程
- **GET /api/v2/courses/{id}/** - 獲取課程詳情
- **PUT /api/v2/courses/{id}/** - 更新課程
- **PATCH /api/v2/courses/{id}/** - 部分更新課程
- **DELETE /api/v2/courses/{id}/** - 刪除課程
- **GET /api/v2/courses/{id}/schedules/** - 獲取課程時間表
- **GET /api/v2/courses/{id}/assignments/** - 獲取課程作業
- **GET /api/v2/courses/{id}/exams/** - 獲取課程考試
- **GET /api/v2/courses/{id}/notes/** - 獲取課程筆記

### 作業 API

- **GET /api/v2/assignments/** - 獲取作業列表
- **POST /api/v2/assignments/** - 創建新作業
- **GET /api/v2/assignments/{id}/** - 獲取作業詳情
- **PUT /api/v2/assignments/{id}/** - 更新作業
- **PATCH /api/v2/assignments/{id}/** - 部分更新作業
- **DELETE /api/v2/assignments/{id}/** - 刪除作業

### 考試 API

- **GET /api/v2/exams/** - 獲取考試列表
- **POST /api/v2/exams/** - 創建新考試
- **GET /api/v2/exams/{id}/** - 獲取考試詳情
- **PUT /api/v2/exams/{id}/** - 更新考試
- **PATCH /api/v2/exams/{id}/** - 部分更新考試
- **DELETE /api/v2/exams/{id}/** - 刪除考試

### 筆記 API

- **GET /api/v2/notes/** - 獲取筆記列表
- **POST /api/v2/notes/** - 創建新筆記
- **GET /api/v2/notes/{id}/** - 獲取筆記詳情
- **PUT /api/v2/notes/{id}/** - 更新筆記
- **PATCH /api/v2/notes/{id}/** - 部分更新筆記
- **DELETE /api/v2/notes/{id}/** - 刪除筆記

### 文件 API

- **GET /api/v2/files/** - 獲取文件列表
- **POST /api/v2/files/** - 上傳新文件
- **GET /api/v2/files/{id}/** - 獲取文件詳情
- **DELETE /api/v2/files/{id}/** - 刪除文件

## 請求和響應示例

### 創建課程

**請求**

```http
POST /api/v2/courses/
Content-Type: application/json

{
  "title": "程式設計",
  "description": "學習Python程式設計的基礎課程",
  "instructor": "王老師",
  "classroom": "資訊大樓301",
  "schedules": [
    {
      "day_of_week": 1,
      "start_time": "09:00:00",
      "end_time": "12:00:00"
    },
    {
      "day_of_week": 3,
      "start_time": "14:00:00",
      "end_time": "17:00:00"
    }
  ]
}
```

**響應**

```json
{
  "id": 1,
  "title": "程式設計",
  "description": "學習Python程式設計的基礎課程",
  "instructor": "王老師",
  "classroom": "資訊大樓301",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "created_by": 1,
  "schedules": [
    {
      "id": 1,
      "day_of_week": 1,
      "start_time": "09:00:00",
      "end_time": "12:00:00"
    },
    {
      "id": 2,
      "day_of_week": 3,
      "start_time": "14:00:00",
      "end_time": "17:00:00"
    }
  ]
}
```

### 上傳文件

**請求**

```http
POST /api/v2/files/
Content-Type: multipart/form-data

{
  "file": (binary data),
  "note": 1,
  "name": "lecture_notes.pdf"
}
```

**響應**

```json
{
  "id": 1,
  "file": "/media/uploads/lecture_notes.pdf",
  "note": 1,
  "name": "lecture_notes.pdf",
  "uploaded_at": "2023-12-01T10:30:00Z",
  "uploaded_by": 1
}
```

## 過濾和排序

所有列表API都支持過濾和排序功能：

- **搜索**：使用 `?search=關鍵詞` 進行搜索
- **排序**：使用 `?ordering=字段名` 進行排序，使用 `-字段名` 進行降序排序

例如：

```
GET /api/v2/courses/?search=程式設計&ordering=-created_at
```

## 分頁

所有列表API都支持分頁功能：

```
GET /api/v2/courses/?page=1&page_size=10
```

響應中會包含分頁信息：

```json
{
  "count": 100,
  "next": "http://example.com/api/v2/courses/?page=2&page_size=10",
  "previous": null,
  "results": [...]
}
```

## 錯誤處理

API使用標準的HTTP狀態碼表示錯誤：

- **400 Bad Request** - 請求格式錯誤
- **401 Unauthorized** - 未認證
- **403 Forbidden** - 權限不足
- **404 Not Found** - 資源不存在
- **500 Internal Server Error** - 服務器錯誤

錯誤響應格式：

```json
{
  "detail": "錯誤信息"
}
```

或者字段錯誤：

```json
{
  "field_name": [
    "錯誤信息"
  ]
}
```