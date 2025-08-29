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
