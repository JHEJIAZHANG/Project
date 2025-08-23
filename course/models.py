from django.db import models
from user.models import LineProfile

class Course(models.Model):
    owner           = models.ForeignKey(LineProfile, on_delete=models.CASCADE)
    name            = models.CharField(max_length=100)
    section         = models.CharField(max_length=50, blank=True)
    description     = models.TextField(blank=True)
    gc_course_id    = models.CharField(max_length=100, unique=True)
    enrollment_code = models.CharField(max_length=50, blank=True)
    course_state    = models.CharField(max_length=20, default='ACTIVE')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Homework(models.Model):
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    owner           = models.ForeignKey(LineProfile, on_delete=models.CASCADE)
    title           = models.CharField(max_length=200)
    description     = models.TextField(blank=True)
    gc_homework_id  = models.CharField(max_length=100, unique=True)
    gc_course_id    = models.CharField(max_length=100)  # 對應的Google Classroom課程ID
    state           = models.CharField(max_length=20, default="PUBLISHED")  # PUBLISHED, DRAFT
    work_type       = models.CharField(max_length=20, default="ASSIGNMENT")  # ASSIGNMENT, QUIZ
    due_date        = models.DateField(null=True, blank=True)
    due_time        = models.TimeField(null=True, blank=True)
    max_points      = models.IntegerField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', 'due_date']),
            models.Index(fields=['owner', 'state']),
        ]




class CourseSchedule(models.Model):
    """
    課程時段設定：用於將筆記依時間自動歸類到對應課程
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules")
    # 0=Monday ... 6=Sunday
    day_of_week = models.IntegerField(choices=[
        (0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["day_of_week", "start_time", "end_time"]),
        ]

    def __str__(self):
        return f"{self.course.name} [{self.day_of_week} {self.start_time}-{self.end_time}]"


class StudentNote(models.Model):
    """
    學生上傳的課程筆記（文字或圖片），可依時間或課程名稱自動歸類
    """
    author = models.ForeignKey(LineProfile, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)  # 筆記對應的時間（可用於自動歸類）
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    classified_by = models.CharField(max_length=16, default="none")  # none | time | name
    note_type = models.CharField(max_length=50, blank=True, default="")  # 自由分類如：課堂筆記、作業筆記等
    tags = models.CharField(max_length=200, blank=True, default="")  # 標籤，用逗號分隔
    priority = models.CharField(max_length=20, blank=True, default="")  # 優先級：低、普通、高等
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Note by {self.author_id} -> {self.course_id or 'unassigned'}"
