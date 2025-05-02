```mermaid
erDiagram
    USER ||--o{ COURSE_SCHEDULE : "有課表"
    USER ||--o{ TASK : "擁有任務"
    USER ||--o{ MARKETPLACE_ITEM : "銷售物品"
    USER ||--o{ COMMUNITY_POST : "發布貼文"
    USER ||--o{ COMMUNITY_COMMENT : "發表留言"
    USER ||--o{ POST_LIKE : "喜歡貼文"
    USER ||--o{ POST_BOOKMARK : "收藏貼文"
    USER ||--o{ CHAT_MESSAGE : "發送訊息"
    USER ||--o{ USER_PREFERENCE : "有偏好設定"
    USER ||--o{ USER_CHAT_ROOM : "是成員"

    COURSE_SCHEDULE }|--|| COURSE : "連結課程"

    MARKETPLACE_ITEM }o--|| CATEGORY : "屬於分類 (可選)"

    COMMUNITY_POST ||--o{ COMMUNITY_COMMENT : "有留言"
    COMMUNITY_POST }o--|| CATEGORY : "屬於分類 (可選)"

    COMMUNITY_COMMENT ||--o{ COMMENT_LIKE : "被喜歡"

    POST_LIKE }o--|| COMMUNITY_POST : "喜歡貼文"
    COMMENT_LIKE }o--|| COMMUNITY_COMMENT : "喜歡留言"

    POST_BOOKMARK }o--|| COMMUNITY_POST : "收藏貼文"

    CHAT_MESSAGE ||--|| CHAT_ROOM : "屬於聊天室"
    USER_CHAT_ROOM ||--|| CHAT_ROOM : "連結聊天室"


    USER {
        int id PK "主鍵"
        string username "使用者名稱 (唯一)"
        string password_hash "密碼雜湊值"
        string email "電子郵件 (唯一)"
        string first_name "名字 (來自註冊)"
        string student_id "學號 (來自註冊, 唯一)"
        datetime date_joined "加入日期"
        bool is_active "是否啟用"
        # ... 其他 Django User 預設欄位
    }

    COURSE {
        int id PK "主鍵"
        string name "課程名稱"
        string code "課程代碼 (可選)"
        string instructor "授課教師 (可選)"
        string location "上課地點"
        # 或許獨立的 Schedule 表更好
    }

    COURSE_SCHEDULE {
         int id PK "主鍵"
         int user_id FK "使用者 ID (外鍵)"
         int course_id FK "課程 ID (外鍵, 可選)"
         string day_of_week "星期幾"
         time start_time "開始時間"
         time end_time "結束時間"
         string course_name "課程名稱 (直接儲存)"
         string location "上課地點 (直接儲存)"
    }

     USER_PREFERENCE {
        int id PK "主鍵"
        int user_id FK "使用者 ID (外鍵, 唯一)"
        string theme "'system', 'light', 'dark'"
        bool notifications_all "所有通知"
        bool notifications_course "課程通知"
        # ... 其他偏好設定
    }

    TASK {
        int id PK "主鍵"
        int user_id FK "使用者 ID (外鍵)"
        string title "標題"
        string description "描述 (可選)"
        datetime due_date "截止日期 (可選)"
        string priority "'high', 'medium', 'low' (優先級)"
        string category "'study', 'club', 'personal', etc. (分類)"
        bool is_completed "是否完成"
        datetime created_at "建立時間"
        datetime updated_at "更新時間"
    }

    CATEGORY {
        int id PK "主鍵"
        string name "分類名稱"
        string type "'marketplace', 'community', 'task' (類型)"
    }

    MARKETPLACE_ITEM {
        int id PK "主鍵"
        int seller_user_id FK "賣家 ID (外鍵)"
        string title "標題"
        string description "描述"
        decimal price "價格"
        string image_url "圖片連結 (可選)"
        int category_id FK "分類 ID (外鍵, 可選)"
        datetime created_at "建立時間"
        datetime updated_at "更新時間"
        string status "'available', 'sold' (狀態)"
    }

    COMMUNITY_POST {
        int id PK "主鍵"
        int author_user_id FK "作者 ID (外鍵, 若匿名可為 NULL)"
        bool is_anonymous "是否匿名"
        string content "內容"
        string image_url "圖片連結 (可選)"
        int category_id FK "分類 ID (外鍵, 可選)"
        datetime created_at "建立時間"
        datetime updated_at "更新時間"
    }

    COMMUNITY_COMMENT {
        int id PK "主鍵"
        int post_id FK "貼文 ID (外鍵)"
        int author_user_id FK "作者 ID (外鍵)"
        string content "內容"
        datetime created_at "建立時間"
        datetime updated_at "更新時間"
    }

    POST_LIKE {
         int id PK "主鍵"
         int user_id FK "使用者 ID (外鍵)"
         int post_id FK "貼文 ID (外鍵)"
         datetime created_at "建立時間"
         UNIQUE (user_id, post_id) "確保一個使用者只能按讚一次"
    }

     COMMENT_LIKE {
         int id PK "主鍵"
         int user_id FK "使用者 ID (外鍵)"
         int comment_id FK "留言 ID (外鍵)"
         datetime created_at "建立時間"
         UNIQUE (user_id, comment_id) "確保一個使用者只能按讚一次"
    }


    POST_BOOKMARK {
         int id PK "主鍵"
         int user_id FK "使用者 ID (外鍵)"
         int post_id FK "貼文 ID (外鍵)"
         datetime created_at "建立時間"
         UNIQUE (user_id, post_id) "確保一個使用者只能收藏一次"
    }

    CHAT_ROOM {
        int id PK "主鍵"
        string name "名稱 (可選, 用於群聊)"
        string type "'direct', 'group' (類型)"
        datetime created_at "建立時間"
    }

     USER_CHAT_ROOM {
        int id PK "主鍵"
        int user_id FK "使用者 ID (外鍵)"
        int room_id FK "聊天室 ID (外鍵)"
        UNIQUE (user_id, room_id) "確保使用者和聊天室的關係唯一"
    }

    CHAT_MESSAGE {
        int id PK "主鍵"
        int room_id FK "聊天室 ID (外鍵)"
        int sender_user_id FK "發送者 ID (外鍵)"
        string content "內容"
        string message_type "'text', 'image' (訊息類型)"
        datetime sent_at "發送時間"
    }
``` 