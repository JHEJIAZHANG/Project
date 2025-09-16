import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from user.models import LineProfile


class CourseV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructor = models.CharField(max_length=100, blank=True, null=True)
    classroom = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, default="#8b5cf6")
    is_google_classroom = models.BooleanField(default=False)
    google_classroom_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(LineProfile, related_name="courses_v2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CourseScheduleV2(models.Model):
    course = models.ForeignKey(CourseV2, related_name="schedules", on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")
    ])  # 0-6 (週日-週六)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} [{self.get_day_of_week_display()} {self.start_time}-{self.end_time}]"


class AssignmentV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(CourseV2, related_name="assignments", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    notification_time = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=[
        ("assignment", "作業"),
        ("project", "專案"),
        ("reading", "閱讀"),
        ("other", "其他")
    ], default="assignment")
    status = models.CharField(max_length=20, choices=[
        ("pending", "待完成"),
        ("completed", "已完成"),
        ("overdue", "已逾期")
    ], default="pending")
    user = models.ForeignKey(LineProfile, related_name="assignments_v2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class ExamV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(CourseV2, related_name="exams", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam_date = models.DateTimeField()
    notification_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(help_text="考試時長（分鐘）")
    location = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, choices=[
        ("midterm", "期中考"),
        ("final", "期末考"),
        ("quiz", "小考"),
        ("other", "其他")
    ], default="other")
    status = models.CharField(max_length=20, choices=[
        ("pending", "待考"),
        ("completed", "已完成"),
        ("overdue", "已結束")
    ], default="pending")
    user = models.ForeignKey(LineProfile, related_name="exams", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class FileAttachment(models.Model):
    """
    已整合至 course.models.FileAttachment
    此模型保留以維持向後相容性，但新功能請使用 course 應用中的版本
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    size = models.IntegerField()
    type = models.CharField(max_length=100)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 可以關聯到不同模型（多態），但也可以獨立存在
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='api_v2_file_attachments')
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = 'api_v2_fileattachment'  # 明確指定表名以避免衝突

    def __str__(self):
        return self.name


class NoteV2(models.Model):
    """
    已整合至 course.models.StudentNote
    此模型保留以維持向後相容性，但新功能請使用 course 應用中的版本
    請遷移至 course.models.StudentNote，功能更完整
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(LineProfile, related_name="notes_v2_deprecated", on_delete=models.CASCADE)
    course = models.ForeignKey(CourseV2, related_name="notes_deprecated", on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    attachments = GenericRelation(FileAttachment)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_v2_notev2'  # 明確指定表名以避免衝突
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =====================
# Custom Todo (自訂分類與待辦)
# =====================

class CustomCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(LineProfile, on_delete=models.CASCADE, related_name='custom_categories')
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=30, blank=True, default='clipboard')
    color = models.CharField(max_length=20, blank=True, default='#3b82f6')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class CustomTodoItem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('overdue', 'overdue'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(LineProfile, on_delete=models.CASCADE, related_name='custom_todos')
    category = models.ForeignKey(CustomCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    course = models.ForeignKey(CourseV2, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_todos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


# =====================
# Learning Recommendation (智慧推薦)
# =====================

class LearningResource(models.Model):
    url = models.URLField(unique=True)
    source = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    snippet = models.TextField(blank=True)
    embedding = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source}:{self.title}"


class AssignmentRecommendation(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    assignment = GenericForeignKey('content_type', 'object_id')

    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"rec:{self.object_id} q={self.query[:20]}"


class AssignmentRecItem(models.Model):
    rec = models.ForeignKey(AssignmentRecommendation, on_delete=models.CASCADE, related_name="items")
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    position = models.IntegerField()

    class Meta:
        ordering = ["position"]
