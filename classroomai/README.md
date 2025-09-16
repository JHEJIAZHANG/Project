# ClassroomAI - 後端 API 與整合說明（提供前端參考）

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-red.svg)](https://www.django-rest-framework.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![LINE Bot](https://img.shields.io/badge/LINE%20Bot-SDK-00C300.svg)](https://developers.line.biz/)
[![Google APIs](https://img.shields.io/badge/Google-APIs-4285F4.svg)](https://developers.google.com/)

## 📖 簡介

本文件為 `Backend/ntub v2/classroomai` 後端服務的完整對接說明，涵蓋：功能清單、API 端點、請求/回應格式、錯誤碼、權限與 OAuth 範圍、整合流程與範例。前端可直接依此文件完成串接。

## 🧭 路由總覽與 Base URLs

- Base URL（開發）：`http://localhost:8000`
- 全域路由入口：見 `classroomai/urls.py`
  - 後端 API 前綴：`/api/`（來自 `user.urls` 與 `course.urls`）
  - LINE Webhook 與內部 API：根於 `/`（來自 `line_bot.urls`）

## 🔐 認證與授權

- 身份來源：LINE 使用者（以 `line_user_id` 辨識）。
- 授權流程：透過 Google OAuth 2.0 取得 Classroom/Calendar 權限，Token 保存在 `LineProfile`。
- 主要 OAuth Scopes（於 `user/_build_google_oauth_url` 明定）：
  - openid、email
  - https://www.googleapis.com/auth/classroom.courses
  - https://www.googleapis.com/auth/classroom.coursework.students
  - https://www.googleapis.com/auth/classroom.coursework.me.readonly
  - https://www.googleapis.com/auth/calendar.events
  - https://www.googleapis.com/auth/classroom.profile.emails
  - https://www.googleapis.com/auth/classroom.rosters.readonly

注意事項：
- 多數 API 以 `line_user_id` 辨識呼叫者，再由後端代持使用者 Google 憑證呼叫 Google API。
- 若憑證失效或 scope 不足，會回傳 401 並附上 `action: relogin` 提示前端引導重新授權。

## 📦 功能模組

- 用戶與綁定：預註冊、Google OAuth、註冊狀態、個人檔案查詢。
- 課程管理：建立課程、列出課程、檢查課程、刪除課程。
- 作業管理：建立/更新/刪除作業、抓取作業列表、繳交統計（含隱私保護與快取）。
- 學生筆記：建立/查詢/詳情/更新/刪除，支援依時間或名稱自動歸類課程、標籤/優先級、搜尋與分頁。
- Google Calendar：事件建立/更新/刪除/查詢、參與者管理。
- LINE Bot 與群綁：Webhook、課程綁定碼、群組綁定管理、AI 回覆推播、Flex 模板渲染。

---

## 👤 用戶與綁定 APIs

所有路徑皆以 `/api/` 為前綴（`user/urls.py`）。

### 1) 預註冊（LIFF）
- 方法/路徑：POST `/api/onboard/pre_register/`
- Body（JSON）：
  - `id_token` string（必填，LIFF 發給的 LINE id_token）
  - `line_user_id` string（必填，需與 id_token.sub 一致）
  - `role` enum: `teacher` | `student`（必填）
  - `name` string（必填）
- 成功 200：
  - `{ "redirectUrl": "https://accounts.google.com/..." }`（導至 Google OAuth 同意畫面）
- 可能錯誤：400 invalid_id_token、429 節流（同一 LINE ID N 分鐘一次，N 由 `settings.REGISTRATION_COOLDOWN_MINUTES`）

### 2) Google OAuth Callback
- 方法/路徑：GET `/api/oauth/google/callback/`
- Query：`code`, `state`（state 為預註冊產生的 UUID）
- 行為：交換 Token、寫入/更新 `LineProfile`、刪除 `Registration`、推播完成訊息、302 轉導到前端成功頁。
- 失敗：400（參數缺失/無效 code）

### 3) 查詢註冊狀態
- 方法/路徑：GET `/api/onboard/status/{line_user_id}/`
- 回應：`{ "registered": true|false }`（以是否有有效 refresh_token 判定）

### 4) 取得個人 Profile
- 方法/路徑：GET `/api/profile/{line_user_id}/`
- 回應：`{ "name": "...", "role": "teacher|student", "email": "..." }`

---

## 🏫 課程與作業 APIs（Google Classroom）

所有路徑皆以 `/api/` 為前綴（`course/urls.py`）。除非特別標註，Content-Type 為 `application/json`。

### 課程

#### 1) 建立課程
- 方法/路徑：POST `/api/classrooms/`
- Body：`{ line_user_id, name, section?, description? }`
- 成功 201：`{ course_id, gc_course_id, enrollmentCode, alternate_link }`
- 備註：`ownerId` 會以呼叫者的 Google email 建立；並推送 LINE Flex 訊息。

#### 2) 取得我的課程列表
- 方法/路徑：GET `/api/courses/?line_user_id=...`
- 成功 200：`{ total_courses, courses: [{ id, name, section, description, ownerId, enrollmentCode, courseState, creationTime, ... }] }`
- 失敗 401：授權失效或 scope 不足 → `{ error, details, action: "relogin" }`

#### 3) 檢查課程狀態
- 方法/路徑：GET `/api/check-course/?course_id=...&line_user_id=...`
- 成功 200：回傳本地與 Google 端是否存在、擁有者、使用者 email/role。
- 失敗 401：Google 授權失敗；404：用戶不存在。

#### 4) 刪除課程
- 方法/路徑：DELETE `/api/delete-course/`
- 參數來源：Body JSON 或 URL Query 皆可（`line_user_id`, `course_id`）
- 成功 200：`{ message: "課程刪除成功", google_classroom_deleted: true, local_database_deleted: bool }`
- 失敗 400/404/409：詳細見回應 `error/message/details`。

### 作業

#### 1) 新增作業（支援多課程）
- 方法/路徑：POST `/api/homeworks/`
- Body：
  - `line_user_id` string
  - `course_id` string（可逗號分隔多個課程 ID）
  - `title` string
  - `due` string（日期，支援多格式；系統以 23:59 為到期時間）
  - `description` string?（可選）
- 成功 201（單一課）：回傳該作業 `coursework_id/title/dueDate/description`。
- 成功 201（多課）：回傳多筆 `results` 與 `errors` 摘要。
- 備註：會推播 LINE Flex 至老師與綁定之群組。

#### 2) 更新作業
- 方法/路徑：PATCH `/api/homeworks/update/`
- Body：`{ line_user_id, course_id, coursework_id, title?, description?, due? }`
- 成功 200：回傳更新後 `id/title/dueDate`。

#### 3) 刪除作業
- 方法/路徑：DELETE `/api/delete_homework/`
- Body：`{ line_user_id, course_id, coursework_id }`
- 成功：204 No Content。

#### 4) 抓取作業列表
- 方法/路徑：GET `/api/get-homeworks/?course_id=cid1,cid2&line_user_id=...`
- 成功 200：
  - `course_summaries`：每課程的作業清單與錯誤
  - `all_homeworks`：扁平陣列（含 `course_id`, `id`, `title`, `description`, `state`, `workType`, `dueDate`, ...）
- 失敗 401：scope 不足 → 要求重新授權。

#### 5) 作業繳交統計（批量、含快取、隱私保護）
- 方法/路徑：GET 或 POST `/api/classroom/submissions/status/`
- 參數二選一：
  - `course_coursework_pairs`: `[{ course_id, coursework_id }]`
  - 或 `course_ids: []` + `coursework_ids: []`（並行陣列）
  - 皆需 `line_user_id`
- 成功 200：回傳教師/學生不同視角的結果摘要；教師結果可能觸發 LINE Flex 統計圖表。
- 失敗 400：參數錯誤；其他錯誤附 `details` 說明。

---

## 📝 學生筆記 APIs

### 1) 建立筆記
- 方法/路徑：POST `/api/notes/`
- Body：`{ line_user_id, text?, image_url?, captured_at?, course_id?, note_type?, tags?, priority? }`
- 邏輯：若提供 `course_id` 直接關聯；否則依時間/文字試圖匹配課程。
- 成功 201：`{ id, course_id?, classified_by, note_type, tags, priority, created_at }`
- 備註：建立後會推送預覽 Flex 訊息給使用者。

### 2) 查詢筆記列表（多條件 + 分頁）
- 方法/路徑：GET `/api/notes/list/`
- Query：
  - `line_user_id`（必填）
  - `course_id?`, `start_date?`, `end_date?`, `classified_by?`, `note_type?`, `priority?`, `tags?`, `search?`
  - `limit?`（預設 20）, `offset?`（預設 0）, `all?=true`（忽略分頁）
- 成功 200：`{ total_count, count, offset, limit, notes: [...] }`

### 3) 取得單筆筆記詳情
- 方法/路徑：GET `/api/notes/detail/?line_user_id=...&note_id=...`
- 成功 200：回傳完整欄位。

### 4) 更新筆記
- 方法/路徑：PATCH/PUT `/api/notes/update/`
- Body：`{ line_user_id, note_id, text?, image_url?, captured_at?, course_id?, note_type?, tags?, priority? }`
- 成功 200：回傳更新欄位與最新內容。

### 5) 刪除筆記
- 方法/路徑：DELETE `/api/notes/delete/`
- 參數來源：Body JSON 或 URL Query（`line_user_id`, `note_id`）
- 成功 200：`{ message: "筆記刪除成功", deleted_note: {...} }`

---

## 📅 Google Calendar APIs

### 1) 建立事件
- 方法/路徑：POST `/api/calendar/create_calendar_event/`
- Body：`{ line_user_id, calendar_id?="primary", summary, description?, start_datetime, end_datetime, location?, attendees? }`
- 成功 201：回傳 `event_id/htmlLink/summary/start/end`；並推送 Flex。

### 2) 更新事件
- 方法/路徑：PATCH `/api/calendar/update_calendar_event/`
- Body：`{ line_user_id, calendar_id?="primary", event_id, summary?, description?, start_datetime?, end_datetime?, location?, attendees? }`
- 成功 200：回傳更新後事件資料。

### 3) 刪除事件
- 方法/路徑：DELETE `/api/calendar/delete_calendar_event/`
- Body：`{ line_user_id, calendar_id?="primary", event_id }`
- 成功 200：`{ message: "Google Calendar 事件刪除成功", event_id, event_summary }`

### 4) 查詢事件
- 方法/路徑：GET `/api/calendar/get_calendar_events/?line_user_id=...&calendar_id=primary&time_min=...&time_max=...&max_results=10`
- 成功 200：`{ events_count, events: [{ id, summary, description, location, start, end, html_link, ... }] }`

### 5) 管理事件參與者
- 方法/路徑：POST `/api/calendar/events/attendees/`
- Body：`{ line_user_id, calendar_id?="primary", event_id, attendees?: [email], attendees_to_remove?: [email] }`
- 成功 200：`{ message: "參與者更新成功", attendees: [...] }`

---

## 💬 LINE Bot 與群綁 APIs

來自 `line_bot/urls.py`，根於 `/`。

### 1) Webhook（LINE 平台觸發）
- 方法/路徑：POST `/line/webhook/`
- 行為：處理 Follow、Postback、文字/多媒體訊息；依使用者/群組情境與角色分流，並可非同步丟給 n8n。

### 2) 產生一次性課程綁定碼（內部）
- 方法/路徑：POST `/internal/api/create-bind-code`
- Body：`{ course_id, line_user_id, course_name?, enrollment_code?, ttl_minutes?=10 }`
- 成功 200：`{ code, course_id, course_name, enrollment_code, expires_at }`
- 備註：資料庫僅儲存雜湊；群組輸入明碼可完成綁定。

### 3) 簡單推播
- 方法/路徑：POST `/internal/api/line/push`
- Body：`{ to, text }`
- 成功 200：`{ ok: true }`

### 4) 群組綁定查詢/建立
- 方法/路徑：
  - GET `/internal/api/group-bindings?group_id=...` → 200 `{ found, group_id, course_id, ... }` 或 404
  - POST `/internal/api/group-bindings` → Body `{ group_id, course_id, line_user_id }`，回 200 綁定資訊；若已綁他課回 409。

### 5) n8n AI 回應入站
- 方法/路徑：POST `/internal/api/n8n/response`
- Body：`{ lineUserId|to, text|output|answer }`
- 成功 200：會將清理後的純文字推送給使用者，並儲存對話。

### 6) 統一 Flex 模板渲染
- 方法/路徑：POST `/line/render-flex/`
- Body：
  - `template_name`：如 `main_menu`、`course_menu`、`homework_menu`、`course_deletion_confirmation(_paginated)`、`student_homework_status` 等
  - `mode`: `template` | `carousel` | `send`
  - `payload`: 視模板而定（例如 `courses` 或 `homeworks` 陣列）
  - `line_user_id` 或 `user_id`: `send` 或 `template` 自動發送時必填
- 成功：回傳渲染內容，或直接推播至 LINE（視 `mode`）。

---

## 🧩 請求/回應通用規範

- Header：`Content-Type: application/json`
- 時區：預設以 `Asia/Taipei` 處理；日期時間採 ISO8601。
- 錯誤格式（範例）：
  - 400：`{ "error": "參數驗證失敗", "errors"|"details": ... }`
  - 401：`{ "error": "Google 授權失效", "details": "...", "action": "relogin" }`
  - 403：`{ "error": "權限不足", "details": "..." }`
  - 404：`{ "error": "Not found" | "用戶不存在" }`
  - 409：`{ "error": "already_bound_other_course", "message": "..." }`
  - 429：`{ "error": "... 分鐘內已送出過申請" }`

---

## 🏗 專案結構（重點檔案）

```
classroomai/
├── classroomai/
│   ├── settings.py
│   ├── urls.py              # 路由總入口（包含 api/ 與 line_bot/）
│   ├── asgi.py / wsgi.py
├── user/                    # 預註冊 / OAuth / Profile
│   ├── views.py
│   ├── urls.py
├── course/                  # 課程 / 作業 / 筆記 / Calendar
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── models.py
├── line_bot/                # Webhook / 綁定碼 / Flex / n8n
│   ├── views.py
│   ├── urls.py
│   ├── utils.py / flex_templates.py
├── templates/after-oauth.html
├── logs/django.log, logs/django_errors.log
└── requirements.txt
```

---

## ⚙️ 環境與部署

### 必要環境變數（.env）
```
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL
DB_NAME=classroomai
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=3306

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://your-domain/api/oauth/google/callback/

# LINE
CHANNEL_SECRET=...
CHANNEL_TOKEN=...
LINE_CHANNEL_ID=...
VITE_LIFF_ID=...

# 外部
N8N_NLP_URL=...
INTERNAL_API_TOKEN=...
```

### 初始化與啟動
```
python -m venv venv
venv\Scripts\activate  # Windows（或 source venv/bin/activate）
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔒 安全與隱私

- 作業繳交統計僅回傳統計摘要；缺交名單存在資料庫短期快取，不會外洩給第三方。
- 綁定碼僅存雜湊，明碼只透過 API 回傳一次供顯示。
- 透過 `line_user_id` 對應 `LineProfile` 的 Google 憑證代呼；請確保前端僅在用戶授權後呼叫需要 Google 資源的 API。

---

## 🧪 測試與診斷

```
python manage.py test
python manage.py test user
python manage.py test course
python manage.py test line_bot
```

---

## 📌 前端整合建議

- 建議在入口進行「註冊狀態檢查」：`GET /api/onboard/status/{line_user_id}/`；未註冊導向 `POST /api/onboard/pre_register/` → 取得 Google OAuth URL → Redirect。
- 呼叫 Classroom/Calendar 相關 API 時，若回 401 並帶 `action: relogin`，彈出重新授權流程。
- 刪除類 API 大多支援「Body 或 Query」帶參數，行動端可依客戶端能力擇一。
- 使用 `get-homeworks` 回傳的 `all_homeworks` 供列表呈現，並搭配 `course_summaries` 製作群組化視圖。
- Flex 模板渲染集中於 `/line/render-flex/`，可由工作流或後端組裝再推播。

---

如需新增欄位或端點，請同步更新本檔，確保前後端對齊。