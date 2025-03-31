from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"PasswordReset({self.user.username}, {self.token})"

# 新增 EmailVerification 模型
class EmailVerification(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)  # 6位數驗證碼
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"EmailVerification({self.email}, {self.code})"
    
# 第三方登入
class UserAuth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_accounts')
    provider = models.CharField(max_length=50)  # 例如 "google"、"line"
    provider_uid = models.CharField(max_length=100)  # 第三方提供的唯一ID
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'provider_uid')

    def __str__(self):
        return f"{self.provider} account for {self.user.username}"
    
# 社交登入日誌（選用，可用於風控）
class SocialLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    provider = models.CharField(max_length=50)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in via {self.provider} at {self.login_time}"

