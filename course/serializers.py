from rest_framework import serializers
from datetime import datetime

class CreateClassSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    name         = serializers.CharField()
    section      = serializers.CharField(required=False, allow_blank=True)
    description  = serializers.CharField(required=False, allow_blank=True)

class CreateHomeworkSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    course_id    = serializers.CharField()
    title        = serializers.CharField()
    due          = serializers.CharField()  # 传入 ISO 或 MM/DD/YY allowerd
    description  = serializers.CharField(required=False, allow_blank=True)

class UpdateHomeworkSerializer(serializers.Serializer):
    line_user_id  = serializers.CharField()
    course_id     = serializers.CharField()
    coursework_id = serializers.CharField()
    title         = serializers.CharField(required=False)
    due           = serializers.CharField(required=False)
    description   = serializers.CharField(required=False, allow_blank=True)

class DeleteHomeworkSerializer(serializers.Serializer):
    line_user_id  = serializers.CharField()
    course_id     = serializers.CharField()
    coursework_id = serializers.CharField()

class DeleteCourseSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    course_id    = serializers.CharField()

class SubmissionsStatusSerializer(serializers.Serializer):
    line_user_id  = serializers.CharField()
    course_id     = serializers.CharField()
    coursework_id = serializers.CharField()

class CreateNoteSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    text = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    captured_at = serializers.DateTimeField(required=False)
    course_id = serializers.CharField(required=False, allow_blank=True)
    note_type = serializers.CharField(required=False, allow_blank=True)  # 自由分類，如：課堂筆記、作業筆記等
    tags = serializers.CharField(required=False, allow_blank=True)       # 標籤，用逗號分隔
    priority = serializers.CharField(required=False, allow_blank=True)   # 優先級，如：低、普通、高

    def validate(self, data):
        if not data.get("text") and not data.get("image_url"):
            raise serializers.ValidationError("text 或 image_url 需擇一")
        return data

class GetNotesSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    course_id = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False) 
    limit = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)
    offset = serializers.IntegerField(required=False, default=0, min_value=0)
    search = serializers.CharField(required=False, allow_blank=True)
    classified_by = serializers.CharField(required=False, allow_blank=True)
    note_type = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.CharField(required=False, allow_blank=True)

class UpdateNoteSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    note_id = serializers.IntegerField()
    text = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    captured_at = serializers.DateTimeField(required=False)
    course_id = serializers.CharField(required=False, allow_blank=True)
    note_type = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # 至少要有一個字段要更新
        update_fields = ['text', 'image_url', 'captured_at', 'course_id', 'note_type', 'tags', 'priority']
        if not any(field in data for field in update_fields):
            raise serializers.ValidationError("至少需要提供一個要更新的字段")
        
        # 如果同時提供了text和image_url，至少其中一個不能為空
        if 'text' in data and 'image_url' in data:
            if not data.get('text') and not data.get('image_url'):
                raise serializers.ValidationError("text 和 image_url 不能同時為空")
        
        return data

class DeleteNoteSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    note_id = serializers.IntegerField()

class GetNoteDetailSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    note_id = serializers.IntegerField()

# Google Calendar Serializers
class CreateCalendarEventSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    calendar_id = serializers.CharField(required=False, default='primary')  # 預設使用主日曆
    summary = serializers.CharField()  # 事件標題
    description = serializers.CharField(required=False, allow_blank=True)
    start_datetime = serializers.DateTimeField()  # 開始時間
    end_datetime = serializers.DateTimeField()    # 結束時間
    location = serializers.CharField(required=False, allow_blank=True)

class UpdateCalendarEventSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    calendar_id = serializers.CharField(required=False, default='primary')
    event_id = serializers.CharField()  # Google Calendar 事件 ID
    summary = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    start_datetime = serializers.DateTimeField(required=False)
    end_datetime = serializers.DateTimeField(required=False)
    location = serializers.CharField(required=False, allow_blank=True)

class DeleteCalendarEventSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    calendar_id = serializers.CharField(required=False, default='primary')
    event_id = serializers.CharField()

class GetCalendarEventsSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    calendar_id = serializers.CharField(required=False, default='primary')
    time_min = serializers.DateTimeField(required=False)  # 查詢開始時間
    time_max = serializers.DateTimeField(required=False)  # 查詢結束時間
    max_results = serializers.IntegerField(required=False, default=10)  # 最大結果數

class ManageCalendarAttendeesSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    calendar_id = serializers.CharField(required=False, default='primary')
    event_id = serializers.CharField()
    attendees = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        help_text="要新增的參與者郵箱列表"
    )
    attendees_to_remove = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        help_text="要移除的參與者郵箱列表"
    )

    def validate(self, data):
        if not data.get('attendees') and not data.get('attendees_to_remove'):
            raise serializers.ValidationError("請提供要新增或移除的參與者。")
        return data

