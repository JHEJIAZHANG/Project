from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordReset, EmailVerification,  UserAuth, SocialLoginLog

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'updated_at')
    search_fields = ('username', 'email')
    ordering = ('username',)


class UserAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_uid', 'created_at')
    search_fields = ('user__username', 'provider', 'provider_uid')
    list_filter = ('provider', 'created_at')


class SocialLoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'login_time', 'ip_address')
    search_fields = ('user__username', 'provider', 'ip_address')
    list_filter = ('provider', 'login_time')

admin.site.register(User, UserAdmin)
admin.site.register(PasswordReset)
admin.site.register(EmailVerification)
admin.site.register(UserAuth, UserAuthAdmin)
admin.site.register(SocialLoginLog, SocialLoginLogAdmin)