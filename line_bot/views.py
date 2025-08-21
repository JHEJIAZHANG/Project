import os, json, requests, secrets, re
from pathlib import Path
from datetime import timedelta

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    LocationMessage, StickerMessage, PostbackEvent
)
from user.models import LineProfile  # 確保這是你的 LineProfile 模型
from .models import OneTimeBindCode, GroupBinding
from line_bot.utils import (
    send_quick_reply,
    send_courses_list,
    send_create_course_guide,
    send_course_binding_success_message,
    send_add_homework_guide,
    send_ask_question_guide,
    hash_code,
)
# FLEX_PATH = Path(__file__).resolve().parent / "flex_templates.json"

# with open(FLEX_PATH, encoding="utf8") as f:
#     FLEX = json.load(f)

# START_REGISTER_FLEX = FLEX["start_register"]
# REGISTER_DONE_FLEX = FLEX["register_done"]
# ── LINE Channel 資訊 ────────────────────────────────────────────────
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_TOKEN  = os.getenv("CHANNEL_TOKEN")


N8N_NLP_URL    = os.getenv("N8N_NLP_URL")

line_bot_api = LineBotApi(CHANNEL_TOKEN)
parser       = WebhookParser(CHANNEL_SECRET)

# ── Flex 設定：簡單直接寫在程式裡；也可改讀 JSON 檔 ────────────────
START_REGISTER_FLEX = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {"type": "text", "text": "歡迎使用智能課程管理系統！", "weight": "bold", "size": "lg"},
            {"type": "text", "text": "點下方按鈕開始註冊", "size": "sm", "color": "#666666"}
        ]
    },
    "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "button",
                "style": "primary",
                "action": {
                    "type": "uri",
                    "label": "開始註冊",
                    "uri": f"https://liff.line.me/{os.getenv('VITE_LIFF_ID')}"
                }
            }
        ]
    }
}

def get_register_done_flex(name: str, role: str) -> dict:
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "0px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                # 頂部漸層背景區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "32px",
                    "paddingBottom": "24px",
                    "backgroundColor": "#4CAF50",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "md",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🎊",
                                    "size": "3xl",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "註冊成功！",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FFFFFF",
                                    "align": "center",
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": f"歡迎 {name} 加入我們",
                                    "size": "md",
                                    "color": "#E8F5E8",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                # 個人資訊卡片
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "lg",
                            "contents": [
                                # 用戶資訊行
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "md",
                                    "paddingAll": "16px",
                                    "backgroundColor": "#F8F9FA",
                                    "cornerRadius": "12px",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 0,
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "👤" if role != 'teacher' else "👨‍🏫",
                                                    "size": "xl"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "flex": 1,
                                            "spacing": "xs",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "身份類型",
                                                    "size": "xs",
                                                    "color": "#6C757D",
                                                    "weight": "bold"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": f"{'🎓 教師' if role == 'teacher' else '📚 學生'}",
                                                    "size": "lg",
                                                    "weight": "bold",
                                                    "color": "#4CAF50"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                # 狀態指示器
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "spacing": "sm",
                                    "paddingAll": "12px",
                                    "backgroundColor": "#E8F5E8",
                                    "cornerRadius": "8px",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "✅",
                                            "flex": 0,
                                            "size": "sm"
                                        },
                                        {
                                            "type": "text",
                                            "text": "帳號綁定完成",
                                            "flex": 1,
                                            "size": "sm",
                                            "color": "#2E7D32",
                                            "weight": "bold"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                # 分隔線
                {
                    "type": "separator",
                    "color": "#E9ECEF",
                    "margin": "none"
                },
                # 下一步指引
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🚀 準備開始使用",
                            "size": "md",
                            "weight": "bold",
                            "color": "#343A40",
                            "align": "center"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "paddingTop": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💬 輸入「建立作業 ...」開始使用",
                                    "size": "sm",
                                    "color": "#6C757D",
                                    "align": "center",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "📋 或輸入「幫助」查看完整功能",
                                    "size": "xs",
                                    "color": "#ADB5BD",
                                    "align": "center",
                                    "wrap": True,
                                    "margin": "xs"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }





# ── Webhook View (callback) ─────────────────────────────────────────
@csrf_exempt
def callback(request):
    signature = request.headers.get("X-Line-Signature")
    body      = request.body.decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return HttpResponseBadRequest("Invalid signature")

    for ev in events:
        # ============ 1. 加好友 → 推註冊 ==============
        if isinstance(ev, FollowEvent):
            line_bot_api.reply_message(
                ev.reply_token,
                FlexSendMessage(alt_text="開始註冊", contents=START_REGISTER_FLEX)
            )

        # ============ 2. Postback 事件 ==============
        elif isinstance(ev, PostbackEvent):
            line_user_id = ev.source.user_id
            postback_data = ev.postback.data
            
            # 處理課程選擇
            if postback_data.startswith("course:"):
                course_id = postback_data.split(":")[1]
                # 這裡可以根據 course_id 做進一步處理
                # 例如發送課程詳細資訊或提供課程相關的選項
                pass

        # ============ 3. 所有訊息事件 ==============
        elif isinstance(ev, MessageEvent):
            # 區分私聊 / 群組；群組訊息不送到 n8n
            source_type = getattr(ev.source, "type", None)
            is_group = (source_type == "group") or hasattr(ev.source, "group_id")
            group_id = getattr(ev.source, "group_id", None)
            line_user_id = getattr(ev.source, "user_id", None)

            # 僅處理文字訊息作為綁定碼（群組）
            if is_group and isinstance(ev.message, TextMessage):
                user_text_raw = ev.message.text or ""
                user_text = user_text_raw.strip().upper()

                # 尋找 6 碼綁定碼（避免 I O 1 0）
                match = re.search(r"\b([A-HJ-NP-Z2-9]{6})\b", user_text)
                if match:
                    code = match.group(1)
                    code_hash_value = hash_code(code)
                    bind_obj = OneTimeBindCode.objects.filter(code_hash=code_hash_value).order_by("-created_at").first()
                    if bind_obj and bind_obj.is_valid():
                        existing = GroupBinding.objects.filter(group_id=group_id).first()
                        if existing:
                            if existing.course_id == bind_obj.course_id:
                                # 已經綁定同一門課，提示即可，不消耗綁定碼
                                line_bot_api.reply_message(
                                    ev.reply_token,
                                    TextSendMessage(text=f"ℹ️ 本群已綁定課程 {existing.course_id}")
                                )
                            else:
                                # 已綁其他課程，禁止更換
                                line_bot_api.reply_message(
                                    ev.reply_token,
                                    TextSendMessage(text=f"❌ 本群已綁定其他課程 {existing.course_id}，如需更換請先解除綁定")
                                )
                        else:
                            # 建立綁定並消耗綁定碼
                            GroupBinding.objects.create(
                                group_id=group_id,
                                course_id=bind_obj.course_id,
                                bound_by_line_user_id=line_user_id or "",
                            )
                            bind_obj.used = True
                            bind_obj.save(update_fields=["used"])

                            line_bot_api.reply_message(
                                ev.reply_token,
                                TextSendMessage(text=f"✅ 群組已綁定課程 {bind_obj.course_id}")
                            )
                            
                            # 發送美觀的課程綁定成功 Flex Message
                            try:
                                send_course_binding_success_message(group_id, bind_obj.course_id, line_user_id or "")
                            except Exception as e:
                                print(f"發送課程綁定 Flex Message 失敗: {e}")
                    else:
                        line_bot_api.reply_message(
                            ev.reply_token,
                            TextSendMessage(text="❌ 綁定碼無效或已過期")
                        )
                # 不論是否匹配到綁定碼，群組訊息都不送 n8n
                continue

            # 私聊：才送到 n8n
            if not is_group:
                # 會員檢查（僅私聊時）
                if not LineProfile.objects.filter(line_user_id=line_user_id).exists():
                    line_bot_api.reply_message(
                        ev.reply_token,
                        FlexSendMessage(alt_text="開始註冊", contents=START_REGISTER_FLEX)
                    )
                    continue

                # 取角色
                role = (
                    LineProfile.objects
                    .filter(line_user_id=line_user_id)
                    .values_list("role", flat=True)
                    .first()
                ) or "unknown"

                # 訊息摘要
                if isinstance(ev.message, TextMessage):
                    user_text = ev.message.text.strip()
                    message_type = "text"
                    message_content = user_text
                    # 顯示載入動畫（可忽略失敗）
                    try:
                        requests.post(
                            url="https://api.line.me/v2/bot/chat/loading/start",
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {CHANNEL_TOKEN}"
                            },
                            json={
                                "chatId": line_user_id,
                                "loadingSeconds": 30
                            },
                            timeout=2
                        )
                    except requests.exceptions.RequestException:
                        pass
                elif isinstance(ev.message, ImageMessage):
                    message_type = "image"
                    message_content = "收到圖片訊息"
                elif isinstance(ev.message, VideoMessage):
                    message_type = "video"
                    message_content = "收到影片訊息"
                elif isinstance(ev.message, AudioMessage):
                    message_type = "audio"
                    message_content = "收到語音訊息"
                elif isinstance(ev.message, FileMessage):
                    message_type = "file"
                    message_content = "收到檔案訊息"
                elif isinstance(ev.message, LocationMessage):
                    message_type = "location"
                    message_content = "收到位置訊息"
                elif isinstance(ev.message, StickerMessage):
                    message_type = "sticker"
                    message_content = "收到貼圖訊息"
                else:
                    message_type = "unknown"
                    message_content = "收到未知類型訊息"

                # 送到 n8n
                payload = {
                    "lineUserId": line_user_id,
                    "rawText": message_content,
                    "role": role,
                    "messageType": message_type,
                    "messageId": getattr(ev.message, "id", None),
                }
                try:
                    requests.post(N8N_NLP_URL, json=payload, timeout=5)
                except requests.exceptions.RequestException:
                    line_bot_api.reply_message(
                        ev.reply_token,
                        FlexSendMessage(
                            alt_text="系統忙碌",
                            contents={
                                "type": "bubble",
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {"type": "text", "text": "系統忙碌中，請稍後再試 🙏", "wrap": True}
                                    ]
                                }
                            }
                        )
                    )
                # 完成私聊處理
                continue

    return HttpResponse("OK", status=200)

# ===== 綁定完成推播（google_callback 用）============================
def push_finish(line_user_id: str):
    try:
        profile = LineProfile.objects.get(pk=line_user_id)
        flex    = get_register_done_flex(profile.name, profile.role)
    except LineProfile.DoesNotExist:
        flex    = get_register_done_flex("使用者", "student")

    line_bot_api.push_message(
        line_user_id,
        FlexSendMessage(alt_text="綁定完成", contents=flex)
    )


# ====== Internal APIs ======================================================

# 產生一次性綁定碼（僅回傳明碼；資料庫只存雜湊）
@csrf_exempt
def api_create_bind_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)

    course_id = (data.get("course_id") or "").strip()
    line_user_id = (data.get("line_user_id") or "").strip()
    ttl_minutes = int(data.get("ttl_minutes") or 10)

    if not course_id or not line_user_id:
        return JsonResponse({"error": "missing course_id / line_user_id"}, status=400)

    # 產生不易混淆的 6 碼
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    plain_code = "".join(secrets.choice(alphabet) for _ in range(6))
    code_hash_value = hash_code(plain_code)

    # 確保唯一（極低機率碰撞）
    for _ in range(5):
        if not OneTimeBindCode.objects.filter(code_hash=code_hash_value).exists():
            break
        plain_code = "".join(secrets.choice(alphabet) for _ in range(6))
        code_hash_value = hash_code(plain_code)

    expires_at = timezone.now() + timedelta(minutes=max(ttl_minutes, 1))

    OneTimeBindCode.objects.create(
        code_hash=code_hash_value,
        course_id=course_id,
        created_by_line_user_id=line_user_id,
        expires_at=expires_at,
        used=False,
    )

    return JsonResponse({
        "code": plain_code,
        "course_id": course_id,
        "expires_at": expires_at.isoformat(),
    })


# 簡單推播 API（to 可以是使用者或群組 ID）
@csrf_exempt
def api_line_push(request):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)

    to = (data.get("to") or "").strip()
    text = (data.get("text") or "").strip()
    if not to or not text:
        return JsonResponse({"error": "missing to / text"}, status=400)

    try:
        line_bot_api.push_message(to, TextSendMessage(text=text))
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# 群組綁定管理：GET 查詢、POST 建立/更新
@csrf_exempt
def api_group_bindings(request):
    if request.method == "GET":
        group_id = (request.GET.get("group_id") or "").strip()
        if not group_id:
            return JsonResponse({"error": "missing group_id"}, status=400)
        obj = GroupBinding.objects.filter(group_id=group_id).first()
        if not obj:
            return JsonResponse({"found": False}, status=404)
        return JsonResponse({
            "found": True,
            "group_id": obj.group_id,
            "course_id": obj.course_id,
            "bound_by_line_user_id": obj.bound_by_line_user_id,
            "bound_at": obj.bound_at.isoformat(),
        })

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8")) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid_json"}, status=400)

        group_id = (data.get("group_id") or "").strip()
        course_id = (data.get("course_id") or "").strip()
        line_user_id = (data.get("line_user_id") or "").strip()
        if not group_id or not course_id or not line_user_id:
            return JsonResponse({"error": "missing group_id / course_id / line_user_id"}, status=400)

        existing = GroupBinding.objects.filter(group_id=group_id).first()
        if existing:
            if existing.course_id != course_id:
                return JsonResponse({
                    "error": "already_bound_other_course",
                    "message": f"本群已綁定課程 {existing.course_id}，請先解除綁定再更換",
                }, status=409)
            # 已綁相同課程，視為冪等
            obj = existing
        else:
            obj = GroupBinding.objects.create(
                group_id=group_id,
                course_id=course_id,
                bound_by_line_user_id=line_user_id,
            )
        return JsonResponse({
            "group_id": obj.group_id,
            "course_id": obj.course_id,
            "bound_by_line_user_id": obj.bound_by_line_user_id,
            "bound_at": obj.bound_at.isoformat(),
        })

    return JsonResponse({"error": "method_not_allowed"}, status=405)