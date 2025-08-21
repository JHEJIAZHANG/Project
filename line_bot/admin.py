from django.contrib import admin
from .models import OneTimeBindCode, GroupBinding


@admin.register(OneTimeBindCode)
class OneTimeBindCodeAdmin(admin.ModelAdmin):
    list_display = ("code_hash", "course_id", "created_by_line_user_id", "expires_at", "used", "created_at")
    list_filter = ("used",)
    search_fields = ("code_hash", "course_id", "created_by_line_user_id")


@admin.register(GroupBinding)
class GroupBindingAdmin(admin.ModelAdmin):
    list_display = ("group_id", "course_id", "bound_by_line_user_id", "bound_at")
    search_fields = ("group_id", "course_id", "bound_by_line_user_id")
