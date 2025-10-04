# user/serializers.py
from rest_framework import serializers


class PreRegisterSerializer(serializers.Serializer):

    line_user_id = serializers.CharField()
    role = serializers.ChoiceField(choices=[("teacher", "teacher"), ("student", "student")])
    name = serializers.CharField()
    id_token = serializers.CharField()
