from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from .models import PasswordReset, EmailVerification
import uuid

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        # 註冊時直接設為啟用，跳過 email 驗證 (僅供測試)
        user.is_active = True 
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # 可為 username 或 email
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')
        user = None
        try:
            user_obj = User.objects.get(username=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
        if not user:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    def validate(self, data):
        try:
            pr = PasswordReset.objects.get(token=data['token'], used=False)
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token")
        # 檢查 token 是否超過1小時
        if pr.created_at < timezone.now() - timezone.timedelta(hours=1):
            raise serializers.ValidationError("Token expired.")
        data['password_reset'] = pr
        return data


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
