from rest_framework import serializers
from .models import (
    CourseV2,
    CourseScheduleV2,
    AssignmentV2,
    ExamV2,
    NoteV2,
    FileAttachment,
    CustomCategory,
    CustomTodoItem,
)
from django.contrib.contenttypes.models import ContentType


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseScheduleV2
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'location']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    schedules = CourseScheduleSerializer(many=True, required=False)

    class Meta:
        model = CourseV2
        fields = ['id', 'title', 'description', 'instructor', 'classroom', 'color', 
                  'is_google_classroom', 'google_classroom_id', 'schedules', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        course = CourseV2.objects.create(**validated_data)
        
        for schedule_data in schedules_data:
            CourseScheduleV2.objects.create(course=course, **schedule_data)
            
        return course

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', None)
        
        # Update course fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update schedules if provided
        if schedules_data is not None:
            # Remove existing schedules
            instance.schedules.all().delete()
            
            # Create new schedules
            for schedule_data in schedules_data:
                CourseScheduleV2.objects.create(course=instance, **schedule_data)
                
        return instance


class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = ['id', 'name', 'size', 'type', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssignmentSerializer(serializers.ModelSerializer):
    attachments = FileAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = AssignmentV2
        fields = ['id', 'course', 'title', 'description', 'due_date', 'notification_time',
                  'type', 'status', 'attachments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamV2
        fields = ['id', 'course', 'title', 'description', 'exam_date', 'notification_time',
                  'duration', 'location', 'type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoteSerializer(serializers.ModelSerializer):
    attachments = FileAttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)
    
    class Meta:
        model = NoteV2
        fields = ['id', 'course', 'title', 'content', 'attachments', 'attachment_ids', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        attachment_ids = validated_data.pop('attachment_ids', [])
        note = NoteV2.objects.create(**validated_data)
        
        # Associate existing attachments with this note
        if attachment_ids:
            content_type = ContentType.objects.get_for_model(NoteV2)
            FileAttachment.objects.filter(id__in=attachment_ids).update(
                content_type=content_type,
                object_id=note.id
            )
            
        return note

    def update(self, instance, validated_data):
        attachment_ids = validated_data.pop('attachment_ids', None)
        
        # Update note fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update attachments if provided
        if attachment_ids is not None:
            # Get content type for NoteV2
            content_type = ContentType.objects.get_for_model(NoteV2)
            
            # Clear existing attachments
            FileAttachment.objects.filter(
                content_type=content_type,
                object_id=instance.id
            ).update(
                content_type=None,
                object_id=None
            )
            
            # Associate new attachments
            FileAttachment.objects.filter(id__in=attachment_ids).update(
                content_type=content_type,
                object_id=instance.id
            )
                
        return instance


class CustomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomCategory
        fields = ['id', 'name', 'icon', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomTodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomTodoItem
        fields = ['id', 'category', 'course', 'title', 'description', 'due_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']