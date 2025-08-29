from django.contrib import admin
from .models import OneTimeBindCode, GroupBinding, ConversationMessage


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
