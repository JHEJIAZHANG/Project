# line_bot/models.py
from django.db import models
from django.utils import timezone


class ConversationMessage(models.Model):
    """
    用戶與Bot的對話訊息記錄
    - line_user_id: 用戶LINE ID
    - message_type: 訊息類型 (user/bot)
    - content: 訊息內容
    - intent: n8n識別的意圖（如果有的話）
    - raw_data: 原始訊息資料（JSON格式）
    - created_at: 建立時間
    """
    
    MESSAGE_TYPES = [
        ('user', '用戶訊息'),
        ('bot', 'Bot回應'),
        ('system', '系統訊息'),
    ]
    
    line_user_id = models.CharField(max_length=50)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    intent = models.CharField(max_length=50, blank=True, null=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['line_user_id', 'created_at']),
            models.Index(fields=['message_type']),
            models.Index(fields=['intent']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.line_user_id} - {self.message_type} - {self.created_at}"


class OneTimeBindCode(models.Model):
    """
    一次性綁定碼（僅存雜湊）
    - code_hash: sha256(明碼)
    - course_id: Google Classroom 課程ID（字串）
    - created_by_line_user_id: 產碼者 LINE userId
    - expires_at: 到期時間（預設 10 分鐘）
    - used: 是否已使用
    - created_at: 建立時間
    """

    code_hash = models.CharField(max_length=128, unique=True)
    course_id = models.CharField(max_length=100)
    course_name = models.CharField(max_length=200, blank=True, default="")
    enrollment_code = models.CharField(max_length=50, blank=True, default="")
    created_by_line_user_id = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code_hash"]),
            models.Index(fields=["expires_at"]),
        ]

    def is_valid(self) -> bool:
        return (not self.used) and (self.expires_at > timezone.now())


class GroupBinding(models.Model):
    """
    LINE 群組與課程綁定
    - group_id: LINE 群組ID（唯一）
    - course_id: Google Classroom 課程ID（字串）
    - bound_by_line_user_id: 綁定者 LINE userId
    - bound_at: 綁定時間
    """

    group_id = models.CharField(max_length=64, unique=True)
    course_id = models.CharField(max_length=100)
    bound_by_line_user_id = models.CharField(max_length=50)
    bound_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["group_id"]),
            models.Index(fields=["course_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.group_id} -> {self.course_id}"


class HomeworkStatisticsCache(models.Model):
    """
    作業統計暫存資料
    - 保護個資：避免將學生資料傳給AI
    - 提高效率：避免重複查詢Google Classroom API
    """
    
    line_user_id = models.CharField(max_length=50, help_text="教師的LINE用戶ID")
    course_id = models.CharField(max_length=100, help_text="Google Classroom課程ID")
    coursework_id = models.CharField(max_length=100, help_text="Google Classroom作業ID")
    course_name = models.CharField(max_length=200, default="", help_text="課程名稱")
    homework_title = models.CharField(max_length=200, default="", help_text="作業標題")
    
    # 統計數據
    total_students = models.IntegerField(default=0)
    submitted_count = models.IntegerField(default=0)
    unsubmitted_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # 缺交學生資料（JSON格式，保護個資）
    unsubmitted_students = models.JSONField(
        default=list,
        help_text="缺交學生列表，包含name, userId, emailAddress"
    )
    
    # 狀態統計
    status_counts = models.JSONField(default=dict, help_text="各種狀態的數量統計")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="資料過期時間（預設1小時）")
    
    class Meta:
        indexes = [
            models.Index(fields=["line_user_id", "created_at"]),
            models.Index(fields=["course_id", "coursework_id"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]
    
    def is_valid(self) -> bool:
        """檢查資料是否仍然有效"""
        return self.expires_at > timezone.now()
    
    @classmethod
    def cleanup_expired(cls):
        """清理所有過期的暫存資料"""
        expired_count = cls.objects.filter(expires_at__lte=timezone.now()).count()
        if expired_count > 0:
            deleted_count, _ = cls.objects.filter(expires_at__lte=timezone.now()).delete()
            print(f"自動清理了 {deleted_count} 筆過期的作業統計暫存資料")
            return deleted_count
        return 0
    
    @classmethod
    def get_valid_cache(cls, line_user_id: str, course_id: str, coursework_id: str):
        """取得有效的暫存資料，同時自動清理過期資料"""
        # 自動清理過期資料（每次查詢時觸發）
        cls.cleanup_expired()
        
        # 返回有效的暫存資料
        return cls.objects.filter(
            line_user_id=line_user_id,
            course_id=course_id,
            coursework_id=coursework_id,
            expires_at__gt=timezone.now()
        ).first()
    
    def __str__(self) -> str:
        return f"{self.line_user_id} - {self.course_name} - {self.homework_title}"
