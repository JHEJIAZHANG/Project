from django.contrib import admin
from .models import CourseV2, CourseScheduleV2, AssignmentV2, ExamV2, NoteV2, FileAttachment


class CourseScheduleInline(admin.TabularInline):
    model = CourseScheduleV2
    extra = 1


@admin.register(CourseV2)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'classroom', 'is_google_classroom', 'created_at')
    search_fields = ('title', 'description', 'instructor', 'classroom')
    list_filter = ('is_google_classroom', 'created_at')
    inlines = [CourseScheduleInline]


@admin.register(AssignmentV2)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'status', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'type', 'created_at')


@admin.register(ExamV2)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_date', 'duration', 'status', 'created_at')
    search_fields = ('title', 'description', 'location')
    list_filter = ('status', 'type', 'created_at')


@admin.register(NoteV2)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'size', 'created_at')
    search_fields = ('name',)
    list_filter = ('type', 'created_at')