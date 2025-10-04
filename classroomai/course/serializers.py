# course/serializers.py
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
    
    # 批量查詢參數
    course_ids    = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="課程ID列表，支援批量查詢"
    )
    coursework_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="作業ID列表，支援批量查詢"
    )
    
    # 批量查詢的課程作業對應關係
    course_coursework_pairs = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="課程作業對應關係列表，格式：[{'course_id': 'xxx', 'coursework_id': 'xxx'}]"
    )
    
    def validate(self, data):
        # 檢查是否提供了有效的查詢參數
        has_batch_query = data.get('course_ids') or data.get('coursework_ids') or data.get('course_coursework_pairs')
        
        if not has_batch_query:
            raise serializers.ValidationError(
                "必須提供批量查詢參數：course_coursework_pairs 或同時提供 course_ids 和 coursework_ids"
            )
        
        # 驗證參數完整性
        if data.get('course_coursework_pairs'):
            # 使用 course_coursework_pairs 時，驗證格式
            for pair in data['course_coursework_pairs']:
                if not pair.get('course_id') or not pair.get('coursework_id'):
                    raise serializers.ValidationError(
                        "course_coursework_pairs 中的每個項目都必須包含 course_id 和 coursework_id"
                    )
        elif data.get('course_ids') and data.get('coursework_ids'):
            # 使用 course_ids + coursework_ids 時，驗證數量匹配
            if len(data['course_ids']) != len(data['coursework_ids']):
                raise serializers.ValidationError(
                    "course_ids 和 coursework_ids 的數量必須相同"
                )
        else:
            raise serializers.ValidationError(
                "批量查詢必須提供 course_coursework_pairs 或同時提供 course_ids 和 coursework_ids"
            )
        
        return data

class CreateNoteSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    title = serializers.CharField(required=False, allow_blank=True)  # 支援 api_v2 的 title 欄位
    content = serializers.CharField(required=False, allow_blank=True)  # 支援 HTML 內容
    text = serializers.CharField(required=False, allow_blank=True)  # 向後相容
    image_url = serializers.URLField(required=False, allow_blank=True)
    captured_at = serializers.DateTimeField(required=False)
    course_id = serializers.CharField(required=False, allow_blank=True)
    note_type = serializers.CharField(required=False, allow_blank=True)  # 自由分類，如：課堂筆記、作業筆記等
    tags = serializers.CharField(required=False, allow_blank=True)       # 標籤，用逗號分隔
    priority = serializers.CharField(required=False, allow_blank=True)   # 優先級，如：低、普通、高

    def validate(self, data):
        if not data.get("title") and not data.get("text") and not data.get("content") and not data.get("image_url"):
            raise serializers.ValidationError("筆記內容不能為空，title、text、content 或 image_url 需擇一")
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
    note_id = serializers.UUIDField()  # 支援 UUID
    title = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)  # 支援 HTML 內容
    text = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    captured_at = serializers.DateTimeField(required=False)
    course_id = serializers.CharField(required=False, allow_blank=True)
    note_type = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # 至少要有一個字段要更新
        update_fields = ['title', 'content', 'text', 'image_url', 'captured_at', 'course_id', 'note_type', 'tags', 'priority']
        if not any(field in data for field in update_fields):
            raise serializers.ValidationError("至少需要提供一個要更新的字段")
        
        # 如果同時提供了text、content和image_url，至少其中一個不能為空
        if ('text' in data or 'content' in data or 'image_url' in data):
            has_content = bool(data.get('title')) or bool(data.get('text')) or bool(data.get('content')) or bool(data.get('image_url'))
            if not has_content:
                raise serializers.ValidationError("title、text、content 和 image_url 不能同時為空")
        
        return data

class DeleteNoteSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    note_id = serializers.UUIDField()  # 支援 UUID

class GetNoteDetailSerializer(serializers.Serializer):
    line_user_id = serializers.CharField()
    note_id = serializers.UUIDField()  # 支援 UUID

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


# 文件附件相關 Serializers
class FileAttachmentSerializer(serializers.Serializer):
    """文件附件序列化器"""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    size = serializers.IntegerField()
    type = serializers.CharField(max_length=100)
    url = serializers.URLField()
    created_at = serializers.DateTimeField(read_only=True)


class CreateFileUploadSerializer(serializers.Serializer):
    """文件上傳序列化器"""
    line_user_id = serializers.CharField()
    name = serializers.CharField(max_length=255)
    size = serializers.IntegerField()
    type = serializers.CharField(max_length=100)
    url = serializers.URLField()
    # 可選關聯到特定筆記
    note_id = serializers.UUIDField(required=False)

