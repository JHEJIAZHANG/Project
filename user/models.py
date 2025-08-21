from django.db import models
import uuid


class Registration(models.Model):
    """
    綁定流程的暫存紀錄（姓名＋LINE ID ＋角色）
    實際資料在 Google OAuth callback 完成後才落到 LineProfile
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    line_user_id = models.CharField(max_length=50)
    role = models.CharField(max_length=10)  # teacher | student
    payload = models.JSONField()            # 目前只放 {"name": ...}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line_user_id} ({self.role})"


class LineProfile(models.Model):
    line_user_id = models.CharField(primary_key=True, max_length=50)
    role = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)

    google_refresh_token = models.TextField(null=True, blank=True)
    google_access_token = models.TextField(null=True, blank=True)      
    google_token_expiry = models.DateTimeField(null=True, blank=True)  

    extra = models.JSONField(default=dict)



