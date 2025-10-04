from django.contrib import admin
from .models import Course, Homework, CourseSchedule, StudentNote

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "owner", "course_state", "created_at")
    list_filter = ("course_state", "created_at")
    search_fields = ("name", "section", "owner__name", "gc_course_id")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('owner', 'name', 'section', 'description')
        }),
        ('Google Classroom', {
            'fields': ('gc_course_id', 'enrollment_code', 'course_state')
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "owner", "state", "due_date", "created_at")
    list_filter = ("state", "work_type", "due_date", "created_at")
    search_fields = ("title", "course__name", "owner__name", "gc_homework_id")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('course', 'owner', 'title', 'description')
        }),
        ('作業詳情', {
            'fields': ('state', 'work_type', 'due_date', 'due_time', 'max_points')
        }),
        ('Google Classroom', {
            'fields': ('gc_homework_id', 'gc_course_id'),
            'classes': ('collapse',)
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CourseSchedule)
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ("course", "get_day_display", "start_time", "end_time", "location")
    list_filter = ("day_of_week", "course")
    search_fields = ("course__name", "location")
    ordering = ("course", "day_of_week", "start_time")
    
    def get_day_display(self, obj):
        return dict(self.model._meta.get_field('day_of_week').choices)[obj.day_of_week]
    get_day_display.short_description = '星期'

@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("author", "course", "note_type", "captured_at", "created_at")
    list_filter = ("note_type", "classified_by", "created_at")
    search_fields = ("author__name", "course__name", "text", "tags")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('author', 'course', 'note_type', 'priority')
        }),
        ('內容', {
            'fields': ('text', 'image_url', 'tags')
        }),
        ('分類資訊', {
            'fields': ('captured_at', 'classified_by'),
            'classes': ('collapse',)
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
