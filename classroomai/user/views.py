# user/views.py  --------------------------------------------------------
import os, json, requests
from urllib.parse import urlencode
from datetime import datetime, timezone as dt_timezone, timedelta
from django.utils import timezone

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from line_bot.views import push_finish
from .models import Registration, LineProfile
from .serializers import PreRegisterSerializer
from .utils import verify_line_id_token
from django.core.exceptions import ValidationError as DjangoValidationError
from uuid import UUID
from linebot.exceptions import LineBotApiError
from django.middleware.csrf import get_token
from django.db.models import Q

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
    # 正確進行 URL 編碼，避免 scope/redirect_uri 等出現空白與特殊字元
    query = urlencode(params)
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


# ---------------------------------------------------------------------
# 1) 預註冊：LIFF 送 line_user_id / role / name
# ---------------------------------------------------------------------
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def pre_register(request):
    ser = PreRegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 標準化 line_user_id，避免前端多帶空白或符號
    line_user_id = ser.validated_data["line_user_id"].strip().rstrip('.')

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
    if payload["sub"] != line_user_id:
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
        line_user_id=line_user_id,
        role=ser.validated_data["role"],
        payload={"name": ser.validated_data["name"]},
    )
    redirect_url = _build_google_oauth_url(str(reg.uuid))
    return Response({"redirectUrl": redirect_url})


# ---------------------------------------------------------------------
# 2.5) Direct Google OAuth URL (不需要預註冊)
# ---------------------------------------------------------------------
@csrf_exempt
@api_view(["POST"]) 
@permission_classes([AllowAny])
@authentication_classes([])
def get_google_oauth_url(request):
    """
    直接獲取 Google OAuth 授權 URL，使用包含用戶數據的 JSON 作為 state
    """
    # 優先從 body 取得；若無則檢查自訂 Header（X-Line-User-Id）
    line_user_id = request.data.get("line_user_id") or request.META.get("HTTP_X_LINE_USER_ID")
    if not line_user_id:
        return Response({"error": "line_user_id is required"}, status=400)
    
    # 從請求中獲取用戶選擇的 role 和 name（如果有的話）
    user_role = request.data.get("role")
    user_name = request.data.get("name")
    
    # 構建包含用戶數據的 state
    state_data = {"line_user_id": line_user_id}
    if user_role:
        state_data["role"] = user_role
    if user_name:
        state_data["name"] = user_name
    
    # 將 state 數據序列化為 JSON 字符串
    state_json = json.dumps(state_data)
    
    redirect_url = _build_google_oauth_url(state_json)
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
    reg = None
    # 標準化 state（去除前後空白與尾端句點）
    state_clean = state.strip().rstrip('.')
    
    # 先嘗試以預註冊的 uuid 查詢（pre_register 以 Registration.uuid 作為 state）
    try:
        state_uuid = UUID(state_clean)
        reg = Registration.objects.get(uuid=state_uuid)
    except (ValueError, DjangoValidationError, Registration.DoesNotExist):
        reg = None

    if reg is None:
        # 如果不是預註冊流程，檢查是否為直接授權（state 為 line_user_id 或包含用戶數據的 JSON）
        try:
            # 嘗試解析 JSON 格式的 state
            try:
                state_data = json.loads(state_clean)
                line_user_id = state_data.get('line_user_id')
                user_role = state_data.get('role')
                user_name = state_data.get('name')
                if not line_user_id:
                    return HttpResponseBadRequest("invalid state: missing line_user_id")
            except json.JSONDecodeError:
                # 如果不是 JSON，檢查是否為純 line_user_id 格式
                if state_clean.startswith('guest-') or state_clean.startswith('U'):
                    line_user_id = state_clean
                    user_role = None
                    user_name = None
                else:
                    return HttpResponseBadRequest("invalid state")
            
            # 創建或獲取用戶 profile
            profile, created = LineProfile.objects.get_or_create(
                line_user_id=line_user_id,
                defaults={
                    'name': user_name or 'Guest User',
                    'role': user_role or 'teacher',
                    'email': ''
                }
            )
            
            # 如果不是新創建的，更新用戶選擇的數據
            if not created and (user_name or user_role):
                if user_name and not profile.name:
                    profile.name = user_name
                if user_role and not profile.role:
                    profile.role = user_role
                profile.save()
            
            # 創建臨時的 reg 對象用於後續處理
            class TempReg:
                def __init__(self, line_user_id, profile):
                    self.line_user_id = line_user_id
                    self.role = profile.role
                    self.payload = {'name': profile.name}
            
            reg = TempReg(line_user_id, profile)
        except Exception:
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
    if hasattr(reg, 'delete'):
        reg.delete()

    # ---------- ⑥ 推播 LINE 告訴使用者綁定完成 ----------
    try:
        push_finish(lp.line_user_id)
    except LineBotApiError as e:
        print(f"Skipping LINE push due to API limit or error: {e}")

    # ---------- ⑦ 302 回你的前端成功頁 ----------
    frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    # 將 email 與 line_user_id 透過查詢參數回傳前端成功頁，便於父頁取得資料
    query = urlencode({
        "email": google_email or "",
        "line_user_id": reg.line_user_id,
    })
    liff_id = os.getenv("LIFF_ID") or os.getenv("NEXT_PUBLIC_LIFF_ID")
    success_path = os.getenv("FRONTEND_SUCCESS_PATH", "/auth/google/success")
    if liff_id:
        deep_query = urlencode({
            "redirect": success_path,
            "email": google_email or "",
            "line_user_id": reg.line_user_id,
        })
        success_url = f"https://liff.line.me/{liff_id}?{deep_query}"
    else:
        # 僅當 success_path 以 '/' 開頭時拼接
        if success_path.startswith('/'):
            success_url = f"{frontend_base_url}{success_path}?{query}"
        else:
            # 後備：若提供了完整 URL，直接使用
            success_url = f"{success_path}?{query}"
    return HttpResponseRedirect(success_url)


# ---------------------------------------------------------------------
# 3) 查詢註冊狀態
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def onboard_status(request, line_user_id: str):
    # 將「已註冊」的判定放寬：
    # - 有 google_refresh_token（離線憑證，最佳指標）
    # - 或有 google_access_token（成功完成一次授權）
    # - 或有 email（callback 已寫入資料）
    # 以避免因首次授權未返還 refresh_token 導致前端一直被導回註冊頁
    exists = LineProfile.objects.filter(line_user_id=line_user_id).filter(
        Q(google_refresh_token__isnull=False) |
        Q(google_access_token__isnull=False) |
        Q(email__isnull=False)
    ).exists()
    return JsonResponse({"registered": exists, "status": "completed" if exists else "pending"})


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


# ---------------------------------------------------------------------
# 5) CSRF token 取得（同時設置 csrftoken cookie 供前端讀取）
# ---------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_csrf_token(request):
    token = get_token(request)
    resp = JsonResponse({"csrfToken": token})
    try:
        resp.set_cookie(
            "csrftoken",
            token,
            max_age=60 * 60 * 24,
            secure=False,
            httponly=False,
            samesite="Lax",
            path="/",
        )
    except Exception:
        pass
    return resp