# ClassroomAI - 智能課程管理系統

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![LINE Bot](https://img.shields.io/badge/LINE%20Bot-SDK-00C300.svg)](https://developers.line.biz/)
[![Google APIs](https://img.shields.io/badge/Google-APIs-4285F4.svg)](https://developers.google.com/)

## 📖 專案概述

ClassroomAI 是一個基於 Django 框架開發的智能課程管理系統，深度整合了 Google Classroom API 和 LINE Bot 服務。系統提供完整的課程管理、作業追蹤、學生筆記、行事曆同步等功能，並透過 n8n 工作流提供智能對話體驗。

### 🎯 核心目標
- 提供教師完整的課程管理解決方案
- 為學生創造便捷的學習體驗
- 整合多個教育服務平台於統一介面
- 透過 AI 對話提供智能化學習輔助

## ✨ 主要功能

### 🔐 用戶認證與授權
- **LINE LIFF 登入**: 使用 LINE ID Token 進行安全身份驗證
- **Google OAuth 2.0**: 完整的 Google 服務授權流程
- **自動 Token 刷新**: 透明的授權令牌管理機制
- **角色權限管理**: 支援教師和學生兩種角色權限

### 🏫 課程管理系統
- **Google Classroom 整合**: 完整的 CRUD 操作支援
- **課程時程設定**: 配置週時間表自動分類筆記
- **學生關係管理**: 課程與學生的多對多關係維護
- **課程綁定機制**: LINE 群組與課程的安全綁定系統

### 📚 作業管理功能
- **多課程作業創建**: 支援一次對多個課程發布作業
- **完整 CRUD 操作**: 創建、查看、更新、刪除作業
- **隱私保護統計**: 作業繳交狀態統計快取機制
- **逾期通知系統**: 自動偵測並通知逾期作業

### 📝 學生筆記系統
- **智能自動分類**: 根據時間或手動指定課程分類
- **多媒體支援**: 支援文字與圖片內容
- **標籤與優先級**: 靈活的筆記標籤和重要程度設定
- **進階搜尋過濾**: 多維度搜尋和篩選功能

### 📅 Google Calendar 整合
- **行事曆事件管理**: 完整的事件 CRUD 操作
- **參與者管理**: 支援事件參與者邀請與管理
- **課程同步**: 自動同步課程時間到個人行事曆

### 🤖 LINE Bot 智能服務
- **Webhook 事件處理**: 即時處理 LINE 訊息事件
- **豐富 Flex Message**: 互動式選單和卡片介面
- **群組綁定系統**: 安全的一次性綁定碼機制
- **n8n AI 整合**: 透過工作流提供智能對話回應

## 🏗️ 技術架構

### 後端框架
- **Django 5.2+**: 主要 Web 框架
- **Django REST Framework 3.15.1**: RESTful API 開發
- **MySQL 8.0+**: 主要資料庫，使用 utf8mb4 編碼
- **Python 3.8+**: 主要程式語言

### 第三方整合服務
- **Google APIs**: Classroom, Calendar, OAuth 2.0 服務
- **LINE Bot SDK**: 聊天機器人和 LIFF 整合
- **n8n**: 工作流程自動化和 NLP 處理平台

### 關鍵技術特性
- **CORS 支援**: 跨域資源共享處理
- **完整日誌系統**: 分層日誌記錄和錯誤追蹤
- **環境變數管理**: 使用 python-dotenv 管理配置
- **時區處理**: 完整的台北時區支援

## 📁 專案結構

```
classroomai/
├── classroomai/                    # 主要專案設定
│   ├── settings.py                 # Django 配置與環境變數
│   ├── urls.py                     # 主要 URL 路由配置
│   ├── asgi.py / wsgi.py          # 部署配置
│   └── __init__.py
├── user/                          # 用戶管理應用
│   ├── models.py                  # LineProfile, Registration 模型
│   ├── views.py                   # 用戶認證與 OAuth 處理
│   ├── serializers.py             # 用戶資料序列化
│   └── utils.py                   # 工具函數
├── course/                        # 課程管理應用
│   ├── models.py                  # Course, Homework, StudentNote, CourseSchedule 模型
│   ├── views.py                   # 課程、作業、筆記 API 視圖
│   ├── serializers.py             # 課程相關資料序列化
│   └── README_student_api.md      # 學生 API 詳細文檔
├── line_bot/                      # LINE Bot 應用
│   ├── models.py                  # ConversationMessage, GroupBinding, BindCode 模型
│   ├── views.py                   # Webhook 處理與訊息路由
│   ├── flex_templates.py          # Flex Message 模板庫
│   ├── middleware.py              # 自定義角色中間件
│   └── utils.py                   # Bot 工具函數
├── logs/                          # 日誌檔案目錄
│   ├── django.log                 # 一般應用日誌
│   └── django_errors.log          # 錯誤日誌
├── requirements.txt               # Python 依賴套件清單
├── manage.py                      # Django 管理命令
├── CLAUDE.md                      # 開發指引與命令參考
└── README.md                      # 專案說明文件
```

## 🚀 安裝與設定

### 系統需求
- **Python 3.8+**
- **MySQL 8.0+** (支援 utf8mb4 編碼)
- **LINE Bot Channel** 和 **LIFF App**
- **Google Cloud Project** (啟用 Classroom 和 Calendar API)
- **n8n 實例** (可選，用於 AI 對話功能)

### 1. 環境準備
```bash
# 克隆專案
git clone <repository-url>
cd classroomai

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 環境變數設定
建立 `.env` 檔案：
```env
# Django 基本設定
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL 資料庫設定
DB_NAME=classroomai
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Google OAuth 2.0 設定
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-domain/api/oauth/google/callback/

# LINE Bot 設定
CHANNEL_SECRET=your_line_channel_secret
CHANNEL_TOKEN=your_line_channel_access_token
LINE_CHANNEL_ID=your_line_channel_id
VITE_LIFF_ID=your_liff_app_id

# 外部服務設定
N8N_NLP_URL=your_n8n_webhook_url
INTERNAL_API_TOKEN=your_internal_api_token
```

### 3. 資料庫初始化
```bash
# 建立資料庫遷移檔案
python manage.py makemigrations

# 執行資料庫遷移
python manage.py migrate

# 建立超級使用者帳號
python manage.py createsuperuser
```

### 4. 啟動開發伺服器
```bash
python manage.py runserver
```

## 🔧 外部服務配置

### Google Cloud Platform 設定
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用以下 API：
   - Google Classroom API
   - Google Calendar API
   - Google OAuth2 API
4. 建立 OAuth 2.0 憑證
5. 設定授權重新導向 URI: `https://your-domain/api/oauth/google/callback/`

### LINE Developers 設定
1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立 Provider 和 Bot Channel
3. 設定 Webhook URL: `https://your-domain/line/webhook/`
4. 建立 LIFF App 用於網頁認證
5. 取得 Channel Secret 和 Channel Access Token

### MySQL 資料庫設定
```sql
-- 建立資料庫 (支援 utf8mb4 編碼)
CREATE DATABASE classroomai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 建立使用者並授予權限
CREATE USER 'classroomai_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON classroomai.* TO 'classroomai_user'@'localhost';
FLUSH PRIVILEGES;
```

## 📱 API 端點說明

### 用戶認證相關
- `POST /api/onboard/pre_register/` - LINE LIFF 用戶預註冊
- `GET /api/oauth/google/callback/` - Google OAuth 回調處理
- `GET /api/onboard/status/<line_user_id>/` - 註冊狀態查詢
- `GET /api/profile/<line_user_id>/` - 用戶個人資料

### 課程管理相關
- `POST /api/classrooms/` - 創建 Google Classroom 課程
- `GET /api/courses/` - 取得用戶課程列表
- `GET /api/check-course/` - 驗證課程存取權限
- `DELETE /api/delete-course/` - 刪除課程

### 作業管理相關
- `POST /api/homeworks/` - 創建作業 (支援多課程)
- `PATCH /api/homeworks/update/` - 更新作業資訊
- `DELETE /api/delete_homework/` - 刪除作業
- `GET /api/get-homeworks/` - 取得課程作業列表 (支援多課程ID，用逗號分隔)
- `GET/POST /api/classroom/submissions/status/` - 作業繳交統計

### 學生筆記相關
- `POST /api/notes/` - 創建學生筆記
- `GET /api/notes/list/` - 筆記列表 (支援篩選)
- `GET /api/notes/detail/` - 單一筆記詳情
- `PATCH /api/notes/update/` - 更新筆記內容
- `DELETE /api/notes/delete/` - 刪除筆記

### Google Calendar 相關
- `POST /api/calendar/create_calendar_event/` - 創建行事曆事件
- `PATCH /api/calendar/update_calendar_event/` - 更新事件
- `DELETE /api/calendar/delete_calendar_event/` - 刪除事件
- `GET /api/calendar/get_calendar_events/` - 取得事件列表
- `POST /api/calendar/events/attendees/` - 管理事件參與者

### LINE Bot 相關
- `POST /line/webhook/` - LINE Bot Webhook 處理
- `POST /internal/api/create-bind-code` - 產生課程綁定碼
- `POST /internal/api/line/push` - 發送 LINE 推播訊息
- `GET/POST /internal/api/group-bindings` - 群組綁定管理
- `POST /internal/api/n8n/response` - n8n AI 回應處理
- `POST /line/render-flex/` - 統一 Flex 模板渲染

詳細的 API 使用說明請參考 `course/README_student_api.md`。

## 🧪 測試與開發

### 執行測試
```bash
# 執行所有測試
python manage.py test

# 測試特定應用
python manage.py test user
python manage.py test course
python manage.py test line_bot

# 檢視測試覆蓋率
coverage run --source='.' manage.py test
coverage report
```

### 開發工具命令
```bash
# 檢查資料庫遷移狀態
python manage.py showmigrations

# 建立新的遷移檔案
python manage.py makemigrations

# 檢查專案設定
python manage.py check

# 收集靜態檔案
python manage.py collectstatic
```

## 📊 資料模型關係

### 核心模型關係圖
```
LineProfile (用戶)
    ├── Course (課程) [1:N]
    ├── StudentNote (筆記) [1:N]
    ├── ConversationMessage (對話) [1:N]
    └── Registration (註冊資料) [1:1]

Course (課程)
    ├── Homework (作業) [1:N]
    ├── CourseSchedule (課程時程) [1:N]
    ├── StudentNote (筆記) [1:N]
    └── GroupBinding (群組綁定) [1:N]

GroupBinding (群組綁定)
    └── OneTimeBindCode (綁定碼) [1:1]
```

### 主要模型說明
- **LineProfile**: 核心用戶模型，儲存 LINE 用戶資訊和 Google OAuth tokens
- **Course**: Google Classroom 課程的本地映射
- **Homework**: 作業管理，支援多種作業類型
- **StudentNote**: 學生筆記系統，支援自動和手動分類
- **GroupBinding**: LINE 群組與課程的安全綁定機制

## 📈 系統監控與日誌

### 日誌配置
```python
# 日誌級別和檔案配置
LOGGING = {
    'version': 1,
    'handlers': {
        'django_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
        'error_file': {
            'level': 'ERROR', 
            'class': 'logging.FileHandler',
            'filename': 'logs/django_errors.log',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_file', 'error_file'],
            'level': 'INFO',
        }
    }
}
```

### 日誌檔案說明
- `logs/django.log` - 一般應用程式日誌
- `logs/django_errors.log` - 錯誤和異常日誌

## 🚀 部署指南

### 生產環境配置
```env
# 生產環境設定
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 資料庫優化
DB_HOST=your-production-db-host
DB_PORT=3306

# 安全性設定
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### 推薦部署架構
- **Web Server**: Nginx (反向代理和靜態檔案)
- **Application Server**: Gunicorn (WSGI 應用伺服器)
- **Database**: MySQL 8.0+ (主要資料庫)
- **Cache**: Redis (會話和快取存儲)
- **Process Manager**: Supervisor (程序監控)

### Docker 部署 (範例)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "classroomai.wsgi:application"]
```

## 🔒 安全性考量

### 資料保護措施
- **作業統計快取**: 保護學生個人繳交資料隱私
- **安全的綁定碼**: 使用雜湊儲存一次性綁定碼
- **Token 管理**: 自動刷新和安全儲存 OAuth tokens
- **權限驗證**: 完整的角色權限檢查機制

### 最佳實務
- 定期更新依賴套件
- 使用 HTTPS 加密通訊
- 實施適當的存取控制
- 定期備份重要資料

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 開發規範
- 遵循 PEP 8 Python 編碼規範
- 為新功能撰寫測試
- 更新相關文檔
- 確保所有測試通過

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

## 📞 支援與聯絡

- **專案 Issues**: [GitHub Issues](link-to-issues)
- **技術文檔**: 請參考各應用目錄下的 README 檔案
- **API 文檔**: `course/README_student_api.md`

## 🙏 致謝

感謝以下開源專案和服務提供者：
- Django 和 Django REST Framework 開發團隊
- LINE Bot SDK 開發者
- Google APIs 團隊
- n8n 社群
- 所有貢獻者和使用者

---

**注意**: 本專案持續開發中，功能和 API 可能會有變更。建議定期查看更新日誌和文檔。