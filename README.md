# ClassroomAI Django Project

This project is a Django-based web application integrating LINE Bot services and a course management system.

## Requirements
- Python 3.11+
- MySQL server

## Setup
1. Clone the repository and change into the project directory:
   ```bash
   git clone <repo-url>
   cd Project
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file at the project root and configure the following variables:
   ```env
   DJANGO_SECRET_KEY=<your_django_secret_key>
   DJANGO_DEBUG=True
   DB_NAME=<database_name>
   DB_USER=<database_user>
   DB_PASSWORD=<database_password>
   DB_HOST=localhost
   DB_PORT=3306
   GOOGLE_CLIENT_ID=<google_client_id>
   GOOGLE_CLIENT_SECRET=<google_client_secret>
   GOOGLE_REDIRECT_URI=<https://your-domain/api/oauth/google/callback/>
   VITE_LIFF_ID=<liff_id>
   CHANNEL_SECRET=<line_channel_secret>
   CHANNEL_TOKEN=<line_channel_access_token>
   LINE_CHANNEL_ID=<line_channel_id>
   N8N_NLP_URL=<n8n_nlp_url>
   INTERNAL_API_TOKEN=<internal_api_token>
   ```
4. Apply migrations and start the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Development
- Run basic checks:
  ```bash
  python manage.py check
  ```

## License
This project is provided as-is without a specific license.


---

## 說明 (繁體中文)

這是一個使用 Django 開發的網頁應用程式，整合 LINE Bot 與課程管理功能。

### 需求
- Python 3.11+
- MySQL 伺服器

### 建置步驟
1. 下載並進入專案資料夾：
   ```bash
   git clone <repo-url>
   cd Project
   ```
2. 建立虛擬環境並安裝套件：
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. 在專案根目錄建立 `.env` 檔，設定必要的環境變數（詳見上方範例）。
4. 執行資料庫遷移並啟動開發伺服器：
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
5. 開發過程可使用 `python manage.py check` 檢查設定是否正確。

