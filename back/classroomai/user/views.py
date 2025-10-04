# user/views.py  --------------------------------------------------------
import os, json, requests
from datetime import datetime, timezone as dt_timezone, timedelta
from django.utils import timezone

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from line_bot.views import push_finish
from .models import Registration, LineProfile
from .serializers import PreRegisterSerializer
from .utils import verify_line_id_token
from django.core.exceptions import ValidationError as DjangoValidationError

# ---------------------------------------------------------------------
# helper：組 Google OAuth URL
# ---------------------------------------------------------------------
def _build_google_oauth_url(state: str) -> str:
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "scope": " ".join(
            [
                "openid",
                "email",
                "https://www.googleapis.com/auth/classroom.courses",
                "https://www.googleapis.com/auth/classroom.coursework.students",
                "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
                "https://www.googleapis.com/auth/calendar.events",
                # 需要補充的 Classroom 權限，才能查到學生姓名與 email
                "https://www.googleapis.com/auth/classroom.profile.emails",
                "https://www.googleapis.com/auth/classroom.rosters.readonly",
            ]
        ),
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


# ---------------------------------------------------------------------
# 1) 預註冊：LIFF 送 line_user_id / role / name
# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def pre_register(request):
    ser = PreRegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 1️⃣ LINE id_token 驗簽
    try:
        payload = verify_line_id_token(ser.validated_data["id_token"])
    except DjangoValidationError as e:
        return Response({
            "error": "invalid_id_token",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return Response({
            "error": "invalid_id_token",
            "message": "LINE id_token 驗證失敗",
            "details": str(e)
        }, status=400)
    if payload["sub"] != ser.validated_data["line_user_id"]:
        return Response({"error": "line_user_id 與 id_token 不符"}, status=400)

    # 2️⃣ 防灌水 ─ 同一 LINE ID N 分鐘內只允許一次
    recent_cutoff = timezone.now() - timedelta(minutes=settings.REGISTRATION_COOLDOWN_MINUTES)
    exists = Registration.objects.filter(
        line_user_id=payload["sub"], created_at__gte=recent_cutoff
    ).exists()
    if exists:
        return Response(
            {"error": f"{settings.REGISTRATION_COOLDOWN_MINUTES} 分鐘內已送出過申請"},
            status=429,
        )

    # 3️⃣ 建立 Registration
    reg = Registration.objects.create(
        line_user_id=payload["sub"],
        role=ser.validated_data["role"],
        payload={"name": ser.validated_data["name"]},
    )
    redirect_url = _build_google_oauth_url(str(reg.uuid))
    return Response({"redirectUrl": redirect_url})


# ---------------------------------------------------------------------
# 2) Google OAuth Callback
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def google_callback(request):
    code  = request.GET.get("code")
    state = request.GET.get("state")
    if not (code and state):
        return HttpResponseBadRequest("missing code / state")

    # ---------- ① 驗證 state ----------
    try:
        reg = Registration.objects.get(pk=state)
    except Registration.DoesNotExist:
        return HttpResponseBadRequest("invalid state")

    # ---------- ② 用 code 換 token ----------
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        },
        timeout=10,
    ).json()
    if "error" in token_res:
        return HttpResponseBadRequest(token_res.get("error_description", "token error"))

    access_token  = token_res["access_token"]
    expires_in    = int(token_res["expires_in"])
    expiry_dt     = datetime.utcnow().replace(tzinfo=dt_timezone.utc) + timedelta(seconds=expires_in)
    refresh_token = token_res.get("refresh_token")          # 首次授權才會有

    # ---------- ③ 解析 id_token 拿 email ----------
    info         = requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={token_res['id_token']}",
        timeout=10,
    ).json()
    google_email = info.get("email")

    # ---------- ④ 建立 / 更新 LineProfile ----------
    lp, _ = LineProfile.objects.update_or_create(
        line_user_id = reg.line_user_id,
        defaults = {
            "role"                  : reg.role,
            "name"                  : reg.payload["name"],
            "email"                 : google_email,
            "google_refresh_token"  : refresh_token or LineProfile.objects
                                         .filter(line_user_id=reg.line_user_id)
                                         .values_list("google_refresh_token", flat=True)
                                         .first(),
            "google_access_token"   : access_token,
            "google_token_expiry"   : expiry_dt,
            "extra"                 : {},
        },
    )

    # ---------- ⑤ 刪掉這筆 Registration，防止重放 ----------
    reg.delete()

    # ---------- ⑥ 推播 LINE 告訴使用者綁定完成 ----------
    push_finish(lp.line_user_id)

    # ---------- ⑦ 302 回你的前端成功頁 ----------
    success_url = (
        "https://f71d345c119f.ngrok-free.app/after-oauth.html"
        "?liff_id=2007818452-Lx2ny6bA&status=success"
    )
    return HttpResponseRedirect(success_url)


# ---------------------------------------------------------------------
# 3) 查詢註冊狀態
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def onboard_status(request, line_user_id: str):
    exists = LineProfile.objects.filter(
        line_user_id=line_user_id,
        google_refresh_token__isnull=False,   # ★ 真的綁定好
    ).exists()
    return JsonResponse({"registered": exists})


# ---------------------------------------------------------------------
# 4) 取得個人 Profile（Success / AlreadyRegistered 用）
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def get_profile(request, line_user_id):
    try:
        obj = LineProfile.objects.get(line_user_id=line_user_id)
        return JsonResponse({
            "name": obj.name,
            "role": obj.role,
            "email": obj.email or "",
        })
    except LineProfile.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

