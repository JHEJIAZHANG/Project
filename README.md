# ClassroomAI - 智能課程管理系統

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 專案概述

ClassroomAI 是一個基於 Django 框架開發的智能課程管理系統，整合了 Google Classroom API 和 LINE Bot 服務。該系統旨在為教師和學生提供一個便捷、智能的課程管理平台，支援課程創建、作業管理、筆記整理、行事曆同步等功能。

### 🎯 主要目標
- 簡化教師的課程管理流程
- 提供學生便捷的學習體驗
- 整合多個教育服務平台
- 實現智能化的課程內容分類

## ✨ 功能特色

### 🏫 課程管理
- **Google Classroom 整合**: 自動同步課程資訊、學生名單、作業等
- **課程創建**: 支援課程名稱、章節、描述等詳細資訊設定
- **課程時程**: 可設定課程時間表，自動歸類筆記和作業
- **群組綁定**: LINE 群組與 Google Classroom 課程自動綁定

### 📚 作業管理
- **作業創建**: 支援多種作業類型（作業、測驗）
- **截止日期管理**: 自動提醒和截止日期追蹤
- **繳交狀態追蹤**: 即時監控學生作業繳交情況
- **評分系統**: 支援分數設定和評分記錄

### 📝 筆記系統
- **智能分類**: 根據時間、課程名稱自動歸類筆記
- **多媒體支援**: 支援文字和圖片筆記
- **標籤系統**: 靈活的標籤和分類管理
- **優先級設定**: 可設定筆記重要程度

### 📅 行事曆整合
- **Google Calendar 同步**: 自動同步課程時間和重要事件
- **事件管理**: 創建、更新、刪除行事曆事件
- **參與者管理**: 支援課程參與者邀請和管理

### 🤖 LINE Bot 服務
- **智能對話**: 自然語言處理和智能回應
- **功能選單**: 豐富的 Flex Message 介面
- **推播通知**: 重要事件和截止日期提醒
- **群組管理**: 支援群組聊天和課程綁定

### 🔐 用戶認證
- **LINE 登入**: 使用 LINE ID 進行身份驗證
- **Google OAuth**: 整合 Google 服務的授權認證
- **角色管理**: 支援教師和學生兩種角色
- **安全機制**: 完整的權限驗證和資料保護

## 🏗️ 技術架構

### 後端框架
- **Django 5.2+**: 主要的 Web 框架
- **Django REST Framework**: API 開發框架
- **MySQL**: 主要資料庫
- **SQLite**: 本地快取和配置存儲

### 第三方整合
- **Google APIs**: Classroom, Calendar, OAuth
- **LINE Bot SDK**: 聊天機器人服務
- **N8N**: 工作流程自動化
- **CORS**: 跨域資源共享支援

### 開發工具
- **Python 3.8+**: 主要程式語言
- **Virtual Environment**: 虛擬環境管理
- **Requirements.txt**: 依賴套件管理
- **Logging**: 完整的日誌記錄系統

## 📁 專案結構

```
classroomai/
├── classroomai/                 # Django 專案設定
│   ├── __init__.py
│   ├── settings.py             # 專案配置
│   ├── urls.py                 # 主要 URL 路由
│   ├── asgi.py                 # ASGI 配置
│   └── wsgi.py                 # WSGI 配置
├── user/                       # 用戶管理應用
│   ├── models.py               # 用戶資料模型
│   ├── views.py                # 用戶相關視圖
│   ├── serializers.py          # 資料序列化
│   └── utils.py                # 工具函數
├── course/                     # 課程管理應用
│   ├── models.py               # 課程資料模型
│   ├── views.py                # 課程相關視圖
│   ├── serializers.py          # 資料序列化
│   └── README_student_api.md   # 學生 API 文檔
├── line_bot/                   # LINE Bot 應用
│   ├── models.py               # Bot 資料模型
│   ├── views.py                # Bot 事件處理
│   ├── flex_templates.py       # Flex Message 模板
│   ├── utils.py                # Bot 工具函數
│   └── middleware.py           # 自定義中間件
├── templates/                   # HTML 模板
├── staticfiles/                 # 靜態檔案
├── logs/                       # 日誌檔案
├── manage.py                   # Django 管理腳本
├── requirements.txt            # Python 依賴套件
└── README.md                   # 專案說明文件
```

## 🚀 安裝說明

### 環境需求
- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- LINE Bot Channel
- Google Cloud Platform 專案

### 1. 克隆專案
```bash
git clone <repository-url>
cd classroomai
```

### 2. 建立虛擬環境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 4. 環境變數設定
創建 `.env` 檔案並設定以下變數：
```env
# Django 設定
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 資料庫設定
DB_NAME=classroomai
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Google OAuth 設定
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-domain/api/oauth/google/callback/

# LINE Bot 設定
CHANNEL_SECRET=your_line_channel_secret
CHANNEL_TOKEN=your_line_channel_token
LINE_CHANNEL_ID=your_line_channel_id
VITE_LIFF_ID=your_liff_id

# 其他設定
N8N_NLP_URL=your_n8n_url
INTERNAL_API_TOKEN=your_internal_token
```

### 5. 資料庫遷移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 建立超級用戶
```bash
python manage.py createsuperuser
```

### 7. 啟動開發伺服器
```bash
python manage.py runserver
```

## 🔧 配置說明

### Google Classroom API 設定
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Classroom API
4. 建立 OAuth 2.0 憑證
5. 設定授權的重新導向 URI

### LINE Bot 設定
1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Channel
3. 設定 Webhook URL
4. 取得 Channel Secret 和 Channel Access Token

### 資料庫設定
系統預設使用 MySQL 資料庫，支援 UTF-8 編碼。請確保資料庫已建立並具有適當的權限。

## 📱 使用方式

### 教師端功能
1. **課程創建**: 透過 LINE Bot 或 API 創建新課程
2. **作業管理**: 建立和發布作業，設定截止日期
3. **學生管理**: 查看學生名單和繳交狀態
4. **行事曆同步**: 自動同步課程時間到 Google Calendar

### 學生端功能
1. **課程查看**: 瀏覽已註冊的課程資訊
2. **作業繳交**: 查看作業要求和截止日期
3. **筆記上傳**: 上傳課堂筆記和學習資料
4. **通知接收**: 接收重要事件和截止日期提醒

### LINE Bot 指令
- `/start`: 開始使用系統
- `/register`: 註冊帳號
- `/courses`: 查看課程列表
- `/homework`: 查看作業資訊
- `/help`: 顯示幫助資訊

## 🔌 API 文檔

### 認證端點
- `POST /api/oauth/pre-register/`: 預註冊
- `GET /api/oauth/google/callback/`: Google OAuth 回調

### 課程管理端點
- `POST /api/classrooms/`: 創建課程
- `GET /api/classrooms/`: 獲取課程列表
- `DELETE /api/classrooms/`: 刪除課程

### 作業管理端點
- `POST /api/homework/`: 創建作業
- `GET /api/homework/`: 獲取作業列表
- `PUT /api/homework/`: 更新作業
- `DELETE /api/homework/`: 刪除作業

### 學生資料端點
- `GET /api/student/profile/`: 獲取學生個人資料
- `GET /api/course/students/`: 獲取課程學生列表

詳細的 API 文檔請參考 `course/README_student_api.md` 檔案。

## 🧪 測試

### 執行測試
```bash
python manage.py test
```

### 測試特定應用
```bash
python manage.py test user
python manage.py test course
python manage.py test line_bot
```

## 📊 日誌系統

系統提供完整的日誌記錄功能：
- **一般日誌**: `logs/django.log`
- **錯誤日誌**: `logs/django_errors.log`

日誌級別可透過 `settings.py` 中的 `LOGGING` 配置進行調整。

## 🚀 部署

### 生產環境設定
1. 設定 `DJANGO_DEBUG=False`
2. 配置 HTTPS 憑證
3. 設定適當的 `ALLOWED_HOSTS`
4. 配置生產級資料庫
5. 設定靜態檔案服務

### 推薦部署方式
- **Docker**: 容器化部署
- **Nginx + Gunicorn**: 反向代理和應用伺服器
- **Supervisor**: 程序管理
- **Redis**: 快取和會話存儲

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡資訊

- **專案維護者**: [您的姓名]
- **電子郵件**: [您的郵箱]
- **專案網址**: [專案 URL]

## 🙏 致謝

- Django 開發團隊
- LINE Bot SDK 開發者
- Google Classroom API 團隊
- 所有貢獻者和使用者

## 🎯 擴展功能規劃 - 行動端體驗升級

### 📱 行動端 UI/UX 設計理念

#### iOS 風格設計原則
- **簡潔直觀**: 採用 iOS 設計語言，圓角卡片、適當留白
- **流暢互動**: 手勢操作、平滑過場動畫
- **深色模式**: 支援系統級深色主題切換
- **原生體驗**: 使用 React Native 或 Flutter 實現原生性能

#### 主要頁面架構
1. **首頁儀表板**: 課程卡片網格視圖，顯示今日課程和待辦事項
2. **課表頁面**: 週視圖課表，支援橫向滑動切換週次
3. **課程詳情**: 課程資訊、作業、考試、筆記整合視圖
4. **揪團比對**: 朋友課程時間比對和排程界面
5. **個人檔案**: 用戶設定和統計數據

### 📅 課表功能設計

#### 輸入方式
- **手動輸入**: 表單式課程新增，支援重複課程設定
- **OCR 識別**: 上傳課表圖片，自動識別課程時間和資訊
- **Google Classroom 同步**: 自動從 Classroom 導入課程表

#### 課表視圖
- **週視圖**: 以週為單位的時間軸顯示
- **日視圖**: 詳細的每日課程安排
- **列表視圖**: 簡潔的課程列表顯示
- **月曆視圖**: 傳統月曆格式顯示課程事件

### 👥 揪團比對功能

#### 核心功能
- **朋友邀請**: 透過 LINE 邀請朋友加入比對
- **時間比對**: 自動比對多方空閒時間段
- **衝突檢測**: 標識時間衝突的課程
- **建議時段**: 智能推薦最佳聚會時間

#### 使用流程
1. 用戶發起揪團，選擇要比對的課程時段
2. 系統生成邀請連結，透過 LINE 分享給朋友
3. 朋友接受邀請，匯入自己的課表
4. 系統自動比對並顯示可用時間段
5. 用戶確認最終聚會時間，建立行事曆事件

### 🔄 LINE 整合強化

#### 深度整合功能
- **無縫跳轉**: 從 LINE Chat 直接跳轉對應功能頁面
- **上下文保持**: 保持聊天上下文，返回時維持狀態
- **推播通知**: 重要事件即時推播到 LINE
- **快速操作**: 在 LINE 內快速完成常用操作

#### 自然語言指令擴展
```
# 課程管理
"創建週一9點的數學課"
"刪除週三的物理課"
"查看這週所有課程"

# 作業管理  
"新增下週一要交的作業"
"查詢數學課的作業"
"標記作業已完成"

# 行事曆管理
"新增明天下午3點的會議"
"查看這月的行程"
"調整週五的約會時間"

# 筆記管理
"記錄今天的課堂重點"
"搜尋上週的筆記"
"分享筆記給小明"

# 揪團功能
"發起讀書會揪團"
"比對我和小華的時間"
"確認週六下午聚會"
```

### 🛠️ 技術實現規劃

#### 前端技術棧
- **React Native**: 跨平台行動應用開發
- **React Navigation**: 頁面導航和路由管理
- **Styled Components**: 樣式管理和主題支援
- **TensorFlow.js**: 客戶端 OCR 和 NLP 處理

#### 後端擴展
- **即時通訊**: WebSocket 支援即時更新和通知
- **檔案處理**: 強化圖片和文件上傳下載
- **AI 服務**: 整合更多機器學習功能
- **快取優化**: Redis 加速常用資料存取

#### 資料庫擴展
- **新增揪團相關表**: GroupSession, Participation, TimeSlot
- **優化課表結構**: 支援重複事件和例外設定
- **增強用戶關係**: 朋友系統和權限管理

### 📊 開發里程碑

#### Phase 1: 基礎架構 (4週)
- [ ] 行動端專案初始化
- [ ] 基礎頁面框架搭建
- [ ] LINE 深度整合實現
- [ ] 基本課表功能開發

#### Phase 2: 核心功能 (6週)
- [ ] 課表 OCR 識別功能
- [ ] 自然語言處理增強
- [ ] 揪團比對算法實現
- [ ] 即時通訊基礎建設

#### Phase 3: 體驗優化 (4週)
- [ ] iOS 風格 UI 完善
- [ ] 動畫和互動優化
- [ ] 性能調優和測試
- [ ] 多設備適配完成

#### Phase 4: 上線準備 (2週)
- [ ] 應用商店提交準備
- [ ] 文件和使用指南
- [ ] 監控和分析設置
- [ ] 用戶回饋收集機制

### 🌟 預期效益

1. **用戶體驗提升**: 從純文字互動升級到視覺化操作
2. **使用場景擴展**: 從個人管理延伸到社交協作
3. **粘性增強**: 透過揪團功能增加用戶互動頻率
4. **商業價值**: 為未來增值服務奠定基礎

### 🔍 風險與挑戰

- **技術複雜度**: 多平台整合和即時功能開發
- **性能考量**: 行動端資源限制和優化需求
- **用戶遷移**: 從純文字到圖形界面的過渡體驗
- **維護成本**: 多端代碼同步和更新管理

---

**注意**: 本擴展計畫將與現有 LINE Bot 功能無縫整合，保持向後兼容性。現有用戶可以逐步過渡到新的行動端體驗。

## 📝 更新日誌

### v1.1.0 (規劃中) - 行動端體驗升級
- [ ] 行動應用程式框架搭建
- [ ] 課表管理和 OCR 功能
- [ ] 揪團比對和社交功能
- [ ] 深度 LINE 整合優化
- [ ] iOS 風格設計系統

### v1.0.0 (2024-01-XX)
- 初始版本發布
- 基本課程管理功能
- LINE Bot 整合
- Google Classroom API 整合
- 用戶認證系統

---

**注意**: 本專案仍在積極開發中，功能可能會有所變更。如有問題或建議，請透過 Issues 頁面回報。

