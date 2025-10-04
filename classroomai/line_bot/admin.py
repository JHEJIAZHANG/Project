from django.contrib import admin
from .models import OneTimeBindCode, GroupBinding, ConversationMessage, HomeworkStatisticsCache


@admin.register(OneTimeBindCode)
class OneTimeBindCodeAdmin(admin.ModelAdmin):
    list_display = ("code_hash", "course_id", "created_by_line_user_id", "expires_at", "used", "created_at")
    list_filter = ("used",)
    search_fields = ("code_hash", "course_id", "created_by_line_user_id")


@admin.register(GroupBinding)
class GroupBindingAdmin(admin.ModelAdmin):
    list_display = ("group_id", "course_id", "bound_by_line_user_id", "bound_at")
    search_fields = ("group_id", "course_id", "bound_by_line_user_id")


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("line_user_id", "message_type", "get_short_content", "intent", "created_at")
    list_filter = ("message_type", "intent", "created_at")
    search_fields = ("line_user_id", "content", "intent")
    readonly_fields = ("line_user_id", "message_type", "content", "intent", "raw_data", "created_at")
    list_per_page = 50
    
    def get_short_content(self, obj):
        """顯示縮短的內容預覽"""
        if len(obj.content) > 100:
            return obj.content[:100] + "..."
        return obj.content
    get_short_content.short_description = "內容預覽"


@admin.register(HomeworkStatisticsCache)
class HomeworkStatisticsCacheAdmin(admin.ModelAdmin):
    list_display = (
        "course_name", 
        "homework_title", 
        "line_user_id", 
        "total_students", 
        "submitted_count", 
        "completion_rate", 
        "is_valid_display",
        "created_at",
        "expires_at"
    )
    list_filter = ("created_at", "expires_at")
    search_fields = ("line_user_id", "course_name", "homework_title", "course_id", "coursework_id")
    readonly_fields = ("created_at", "is_valid_display", "time_remaining")
    ordering = ("-created_at",)
    list_per_page = 25
    
    fieldsets = (
        ('課程與作業資訊', {
            'fields': ('course_name', 'homework_title', 'course_id', 'coursework_id')
        }),
        ('教師資訊', {
            'fields': ('line_user_id',)
        }),
        ('統計數據', {
            'fields': ('total_students', 'submitted_count', 'unsubmitted_count', 'completion_rate', 'status_counts')
        }),
        ('缺交學生資料', {
            'fields': ('unsubmitted_students',),
            'classes': ('collapse',)
        }),
        ('時間資訊', {
            'fields': ('created_at', 'expires_at', 'is_valid_display', 'time_remaining'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid_display(self, obj):
        """顯示暫存資料是否有效"""
        if obj.is_valid():
            return "✅ 有效"
        else:
            return "❌ 已過期"
    is_valid_display.short_description = "狀態"
    
    def time_remaining(self, obj):
        """顯示剩餘有效時間"""
        from django.utils import timezone
        if obj.is_valid():
            remaining = obj.expires_at - timezone.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            return "已過期"
    time_remaining.short_description = "剩餘時間"
    
    def get_queryset(self, request):
        """添加自動清理功能到查詢集"""
        # 每次訪問admin頁面時自動清理過期資料
        HomeworkStatisticsCache.cleanup_expired()
        return super().get_queryset(request)
    
    actions = ['cleanup_expired_action']
    
    def cleanup_expired_action(self, request, queryset):
        """手動清理過期資料的admin動作"""
        deleted_count = HomeworkStatisticsCache.cleanup_expired()
        self.message_user(request, f"已清理 {deleted_count} 筆過期的暫存資料")
    cleanup_expired_action.short_description = "清理所有過期的暫存資料"
