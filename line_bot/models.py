from django.db import models
from django.utils import timezone


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
