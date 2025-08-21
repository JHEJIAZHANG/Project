from django.contrib import admin
from .models import Course, Homework, CourseSchedule, StudentNote

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'section', 'gc_course_id', 'enrollment_code', 'created_at')
    list_filter = ('created_at', 'owner__role')
    search_fields = ('name', 'owner__name', 'owner__line_user_id', 'gc_course_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'section', 'description')
        }),
        ('擁有者', {
            'fields': ('owner',)
        }),
        ('Google Classroom', {
            'fields': ('gc_course_id', 'enrollment_code')
        }),
        ('時間資訊', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner', 'state', 'due_date', 'created_at')
    list_filter = ('state', 'work_type', 'due_date', 'created_at', 'owner__role')
    search_fields = ('title', 'course__name', 'owner__name', 'gc_homework_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'description')
        }),
        ('關聯資訊', {
            'fields': ('course', 'owner')
        }),
        ('Google Classroom', {
            'fields': ('gc_homework_id', 'gc_course_id')
        }),
        ('作業設定', {
            'fields': ('state', 'work_type', 'due_date', 'due_time', 'max_points')
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseSchedule)
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ("course", "day_of_week", "start_time", "end_time", "location", "created_at")
    list_filter = ("day_of_week", "course")
    search_fields = ("course__name", "course__gc_course_id", "location")
    ordering = ("course", "day_of_week", "start_time")


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "course", "classified_by", "created_at")
    list_filter = ("classified_by", "course")
    search_fields = ("author__name", "author__line_user_id", "course__name", "text")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
