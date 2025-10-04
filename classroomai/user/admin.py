# user/admin.py
from django.contrib import admin
from .models import LineProfile, Registration

@admin.register(LineProfile)
class LineProfileAdmin(admin.ModelAdmin):
    list_display = ("line_user_id", "name", "role", "email")
    list_filter = ("role",)
    search_fields = ("line_user_id", "name", "email")
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('line_user_id', 'name', 'role', 'email')
        }),
        ('Google 認證', {
            'fields': ('google_refresh_token', 'google_access_token', 'google_token_expiry'),
            'classes': ('collapse',)
        }),
        ('額外資訊', {
            'fields': ('extra',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("uuid", "line_user_id", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("line_user_id", "uuid")
    readonly_fields = ("uuid", "created_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('line_user_id', 'role')
        }),
        ('詳細資料', {
            'fields': ('payload',)
        }),
        ('時間資訊', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
