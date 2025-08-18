from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import (RegisterSerializer, LoginSerializer,
                          ForgotPasswordSerializer, ResetPasswordSerializer,
                          VerifyEmailSerializer)
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from .models import PasswordReset, EmailVerification
from django.utils import timezone
from django.core.mail import send_mail
from .models import UserAuth, SocialLoginLog
import requests
import jwt
from jwt import PyJWKClient
from django.conf import settings
import uuid, random

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 生成6位數驗證碼
            code = str(random.randint(100000, 999999))
            EmailVerification.objects.create(email=user.email, code=code)
            # 建立驗證連結（請根據前端路徑調整）
            verification_link = f"http://your-frontend-domain/verify-email?email={user.email}&code={code}"
            send_mail(
                'Email Verification',
                f"Your verification code is {code}. Alternatively, click the following link to verify your email: {verification_link}",
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({"detail": "User registered. Please check your email to verify your account."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                ev = EmailVerification.objects.filter(email=email, code=code, is_used=False).latest("created_at")
            except EmailVerification.DoesNotExist:
                return Response({"detail": "Invalid or expired verification code."},
                                status=status.HTTP_400_BAD_REQUEST)
            ev.is_used = True
            ev.save()
            try:
                user = User.objects.get(email=email)
                user.is_active = True  # 啟用帳號
                user.save()
            except User.DoesNotExist:
                return Response({"detail": "User not found."},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            # ✅ 加入這段紀錄登入日誌
            SocialLoginLog.objects.create(
                user=user,
                provider='local',  # 表示一般帳密登入
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", "")
            )
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # 檢查過去 24 小時內重置請求次數（每天最多 10 次）
            one_day_ago = timezone.now() - timezone.timedelta(days=1)
            reset_count = PasswordReset.objects.filter(user=user, created_at__gte=one_day_ago).count()
            if reset_count >= 10:
                return Response(
                    {"detail": "Password reset limit exceeded for today"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 將該使用者目前所有未使用的 token 作廢，確保同一時間只保留最新一個 token
            PasswordReset.objects.filter(user=user, used=False).update(used=True)
            
            # 生成新的唯一 token
            token_str = str(uuid.uuid4())
            PasswordReset.objects.create(user=user, token=token_str)
            
            # 發送電子郵件（請將網址替換成你的前端實際域名）
            reset_link = f"http://your-frontend-domain/reset-password?token={token_str}"
            send_mail(
                'Password Reset Request',
                f"Please click the following link to reset your password: {reset_link}",
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({"detail": "Password reset email sent"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            pr = serializer.validated_data['password_reset']
            user = pr.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            pr.used = True
            pr.save()
            return Response({"detail": "Password has been reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SocialLoginView(APIView):
    def post(self, request):
        print("Request data:", request.data)
        provider = request.data.get("provider")
        if not provider:
            return Response({"detail": "Provider is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        provider = provider.lower()
        
        if provider == "google":
            # Google 使用 access_token 驗證
            access_token = request.data.get("access_token")
            if not access_token:
                return Response({"detail": "access_token required for Google login."}, status=status.HTTP_400_BAD_REQUEST)
            google_token_info_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
            resp = requests.get(google_token_info_url, params={"access_token": access_token})
            if resp.status_code != 200:
                return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)
            token_info = resp.json()
            if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
                return Response({"detail": "Invalid Google token (audience mismatch)."}, status=status.HTTP_400_BAD_REQUEST)
            provider_uid = token_info.get("sub")
            email = token_info.get("email")
        
        elif provider == "line":
            # LINE 採用 OAuth2 授權碼流程，後端交換 code 取得 token
            code = request.data.get("code")
            redirect_uri = request.data.get("redirect_uri")
            if not code:
                return Response({"detail": "code required for LINE login."}, status=status.HTTP_400_BAD_REQUEST)
            if not redirect_uri:
                return Response({"detail": "redirect_uri required for LINE login."}, status=status.HTTP_400_BAD_REQUEST)
            
            token_url = "https://api.line.me/oauth2/v2.1/token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINE_CHANNEL_ID,
                "client_secret": settings.LINE_CHANNEL_SECRET,
            }
            token_resp = requests.post(token_url, data=data)
            print("token_resp", token_resp)
            if token_resp.status_code != 200:
                print("LINE token exchange failed:", token_resp.status_code, token_resp.text)
                return Response({"detail": "Failed to exchange LINE token."}, status=status.HTTP_400_BAD_REQUEST)
            token_data = token_resp.json()
            print("token_data", token_data)
            id_token = token_data.get("id_token")
            if not id_token:
                return Response({"detail": "No id_token received from LINE."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 驗證 LINE 的 id_token
            try:
                payload = jwt.decode(
                    id_token,
                    settings.LINE_CHANNEL_SECRET,
                    algorithms=["HS256"],
                    audience=settings.LINE_CHANNEL_ID,
                    issuer="https://access.line.me"
                )
            except jwt.ExpiredSignatureError:
                return Response({"detail": "LINE token expired."}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid LINE token."}, status=status.HTTP_400_BAD_REQUEST)
            
            provider_uid = payload.get("sub")
            email = payload.get("email")
            if not email:
                email = f"{provider_uid}@line.com"
        else:
            return Response({"detail": "Unsupported provider."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 檢查是否已有對應的第三方帳號記錄
        try:
            user_auth = UserAuth.objects.get(provider=provider, provider_uid=provider_uid)
            user = user_auth.user
        except UserAuth.DoesNotExist:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = email.split("@")[0]
                user = User.objects.create_user(username=username, email=email)
                user.is_active = True  # 第三方登入視為已驗證
                user.save()
            UserAuth.objects.create(user=user, provider=provider, provider_uid=provider_uid)
        
        # 記錄登入日誌（IP、User Agent）
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        SocialLoginLog.objects.create(user=user, provider=provider, ip_address=ip_address, user_agent=user_agent)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)

