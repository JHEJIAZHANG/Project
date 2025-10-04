# line_bot/views.py
import os, json, requests, secrets, re, time
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
from .models import OneTimeBindCode, GroupBinding, ConversationMessage
from line_bot.utils import (
    send_courses_list,
    send_create_course_guide,
    send_course_binding_success_message,
    send_add_homework_guide,
    send_ask_question_guide,
    hash_code,
)
from .flex_templates import (get_flex_template, create_custom_carousel, get_start_register_flex, get_register_done_flex, get_available_templates, get_template_categories)







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

# ── Flex 設定 ────────────────────────────────────────────
# 所有 Flex Message 已移動到 flex_templates.py

# 註冊完成處理函數已移動到 flex_templates.py





# ── Webhook View (callback) ─────────────────────────────────────────
@csrf_exempt
def callback(request):
    signature = request.headers.get("X-Line-Signature")
    body      = request.body.decode("utf-8")
    
    # 註解掉系統webhook記錄，避免過多系統訊息
    # try:
    #     ConversationMessage.objects.create(
    #         line_user_id="system_webhook",
    #         message_type="system",
    #         content=f"Webhook received",
    #         raw_data={"signature": signature, "body_length": len(body)}
    #     )
    # except Exception as e:
    #     print(f"儲存webhook記錄失敗: {e}")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return HttpResponseBadRequest("Invalid signature")

    for ev in events:
        # ============ 1. 加好友 → 推註冊 ==============
        if isinstance(ev, FollowEvent):
            start_register_template = get_start_register_flex()
            line_bot_api.reply_message(
                ev.reply_token,
                FlexSendMessage(
                    alt_text=start_register_template["altText"], 
                    contents=start_register_template["contents"]
                )
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
            
            # 🔔 處理自動通知缺交學生
            elif postback_data.startswith("action=notify_unsubmitted"):
                try:
                    # 解析 postback 數據
                    import urllib.parse
                    params = urllib.parse.parse_qs(postback_data)
                    
                    course_id = params.get('course_id', [''])[0]
                    coursework_id = params.get('coursework_id', [''])[0]
                    
                    if not course_id or not coursework_id:
                        line_bot_api.reply_message(
                            ev.reply_token,
                            TextSendMessage(text="❌ 無法取得課程或作業資訊，請重新查詢作業狀態")
                        )
                        continue
                    
                    # 調用從資料庫讀取的自動通知功能
                    from line_bot.utils import notify_unsubmitted_students_from_cache
                    
                    result = notify_unsubmitted_students_from_cache(
                        teacher_line_user_id=line_user_id,
                        course_id=course_id,
                        coursework_id=coursework_id
                    )
                    
                    # 檢查結果並回應
                    if "error" in result:
                        line_bot_api.reply_message(
                            ev.reply_token,
                            TextSendMessage(text=f"❌ {result['error']}\n{result.get('message', '')}")
                        )
                    else:
                        # 成功執行通知
                        total = result.get('total_students', 0)
                        line_notified = result.get('line_notified', 0)
                        email_notified = result.get('email_notified', 0)
                        failed = result.get('failed', 0)
                        
                        success_count = line_notified + email_notified
                        
                        response_text = f"✅ 自動通知已完成\n\n"
                        response_text += f"📊 通知結果：\n"
                        response_text += f"• 成功通知：{success_count}/{total} 位學生\n"
                        response_text += f"• LINE 通知：{line_notified} 位\n"
                        response_text += f"• Email 通知：{email_notified} 位\n"
                        
                        if failed > 0:
                            response_text += f"• 通知失敗：{failed} 位\n"
                        
                        response_text += f"\n💡 詳細通知結果已私訊給您"
                        
                        line_bot_api.reply_message(
                            ev.reply_token,
                            TextSendMessage(text=response_text)
                        )
                    
                except Exception as e:
                    print(f"自動通知處理失敗: {e}")
                    line_bot_api.reply_message(
                        ev.reply_token,
                        TextSendMessage(text=f"❌ 自動通知功能發生錯誤，請稍後再試")
                    )

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
                                send_course_binding_success_message(
                                    group_id, 
                                    bind_obj.course_id, 
                                    line_user_id or "",
                                    bind_obj.course_name,
                                    bind_obj.enrollment_code
                                )
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
                    start_register_template = get_start_register_flex()
                    line_bot_api.reply_message(
                        ev.reply_token,
                        FlexSendMessage(
                            alt_text=start_register_template["altText"], 
                            contents=start_register_template["contents"]
                        )
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
                    
                    # ═══ 檢查是否為功能選單關鍵詞 ═══
                    flex_menu_responses = {
                        # 🏠 主選單相關（所有可能的觸發詞）
                        "功能選單": "main_menu",
                        "選單": "main_menu", 
                        "menu": "main_menu",
                        "主選單": "main_menu",
                        "想知道的都在這裡": "main_menu",
                        
                        # 📚 課程管理相關
                        "課程管理": "course_menu",
                        "查看課程管理功能": "course_menu", 
                        "📚 課程": "course_menu",
                        
                        # 📝 作業管理相關 
                        "作業管理": "homework_menu",
                        "查看作業管理功能": "homework_menu",
                        "📝 作業": "homework_menu",
                        
                        # 📅 行事曆管理相關
                        "行事曆管理": "calendar_menu",
                        "查看行事曆管理功能": "calendar_menu",
                        "📅 行事曆": "calendar_menu",
                        
                        # 📓 筆記管理相關
                        "筆記管理": "notes_menu", 
                        "查看筆記管理功能": "notes_menu",
                        "📓 筆記": "notes_menu",
                        
                        # ⚙️ 帳戶設定相關
                        "帳戶設定": "account_menu",
                        "查看帳戶設定功能": "account_menu",
                        "⚙️ 設定": "account_menu",
                        
                        # ❓ 使用說明相關
                        "使用說明": "system_usage_guide",
                        "查看使用說明": "system_usage_guide",
                        "❓ 說明": "system_usage_guide",
                        "說明": "system_usage_guide",
                        
                        # 📖 各種指南說明
                        "課程建立指南": "course_creation_guide",
                        "如何建立課程": "course_creation_guide",
                        "課程建立步驟": "course_creation_guide", 
                        "建立課程教學": "course_creation_guide",
                        
                        "作業建立指南": "homework_creation_guide",
                        "如何新增作業": "homework_creation_guide",
                        "作業建立步驟": "homework_creation_guide",
                        "新增作業教學": "homework_creation_guide",
                        
                        "系統使用指南": "system_usage_guide",
                        "如何開始使用": "system_usage_guide",
                        "新手指南": "system_usage_guide",
                        "使用教學": "system_usage_guide",
                        "操作說明": "system_usage_guide"
                    }
                    
                    # 如果用戶輸入的是功能選單關鍵詞，直接回覆 Flex Message
                    if user_text in flex_menu_responses:
                        template_name = flex_menu_responses[user_text]
                        template = get_flex_template(template_name)
                        if template:
                            try:
                                line_bot_api.reply_message(
                                    ev.reply_token,
                                    FlexSendMessage(
                                        alt_text=template.get("altText", "功能選單"),
                                        contents=template["contents"]
                                    )
                                )
                                print(f"成功回覆 {template_name} Flex Message 給用戶 {line_user_id}")
                            except Exception as e:
                                try:
                                    line_bot_api.push_message(
                                        line_user_id,
                                        FlexSendMessage(
                                            alt_text=template.get("altText", "功能選單"),
                                            contents=template["contents"]
                                        )
                                    )
                                    print(f"reply 失敗，改以 push 送出 {template_name} 給 {line_user_id}")
                                except Exception as push_error:
                                    print(f"回覆與推送 Flex 皆失敗: {push_error}")
                            finally:
                                continue
                    
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

                # 儲存用戶訊息到資料庫
                try:
                    ConversationMessage.objects.create(
                        line_user_id=line_user_id,
                        message_type="user",
                        content=message_content,
                        raw_data={
                            "message_type": message_type,
                            "message_id": getattr(ev.message, "id", None),
                            "role": role
                        }
                    )
                except Exception as e:
                    print(f"儲存用戶訊息失敗: {e}")
                
                # 送到 n8n（根據角色分流）
                payload = {
                    "lineUserId": line_user_id,
                    "rawText": message_content,
                    "role": role,
                    "messageType": message_type,
                    "messageId": getattr(ev.message, "id", None),
                }
                
                # 根據角色選擇不同的 n8n endpoint
                if role == "teacher":
                    n8n_url = os.getenv("N8N_TEACHER_URL", N8N_NLP_URL)
                elif role == "student":
                    n8n_url = os.getenv("N8N_STUDENT_URL", N8N_NLP_URL)
                else:
                    n8n_url = N8N_NLP_URL
                
                # 非同步發送 n8n 請求，避免阻塞 LINE 回應
                import threading
                def async_n8n_request(url, payload_data):
                    try:
                        requests.post(url, json=payload_data, timeout=10)
                    except requests.exceptions.RequestException:
                        # 記錄錯誤但不影響用戶體驗
                        print(f"n8n 請求失敗: {url}")
                
                # 啟動非執行緒發送請求
                threading.Thread(target=async_n8n_request, args=(n8n_url, payload)).start()
                # 完成私聊處理
                continue

    return HttpResponse("OK", status=200)

# ===== 綁定完成推播（google_callback 用）============================
def push_finish(line_user_id: str):
    # 檢查是否為 guest 用戶，guest 用戶無法接收 LINE 訊息
    if line_user_id.startswith('guest-'):
        print(f"跳過對 guest 用戶 {line_user_id} 發送 LINE 訊息")
        return
    
    try:
        profile = LineProfile.objects.get(pk=line_user_id)
        # 發送註冊成功訊息
        register_done_flex = get_register_done_flex(profile.name, profile.role)
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(
                alt_text=register_done_flex["altText"], 
                contents=register_done_flex["contents"]
            )
        )
        
        # 延遲發送功能選單
        time.sleep(1)  # 等待 1 秒
        
        main_menu_flex = get_flex_template("main_menu")
        if main_menu_flex:
            line_bot_api.push_message(
                line_user_id,
                FlexSendMessage(
                    alt_text=main_menu_flex["altText"], 
                    contents=main_menu_flex["contents"]
                )
            )
            
    except LineProfile.DoesNotExist:
        # 找不到用戶資料時的處理
        register_done_flex = get_register_done_flex("使用者", "student")
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(
                alt_text=register_done_flex["altText"], 
                contents=register_done_flex["contents"]
            )
        )
        
        # 延遲發送功能選單
        time.sleep(1)
        
        main_menu_flex = get_flex_template("main_menu")
        if main_menu_flex:
            line_bot_api.push_message(
                line_user_id,
                FlexSendMessage(
                    alt_text=main_menu_flex["altText"], 
                    contents=main_menu_flex["contents"]
                )
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
    course_name = (data.get("course_name") or "").strip()
    enrollment_code = (data.get("enrollment_code") or "").strip()
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
        course_name=course_name,
        enrollment_code=enrollment_code,
        created_by_line_user_id=line_user_id,
        expires_at=expires_at,
        used=False,
    )

    return JsonResponse({
        "code": plain_code,
        "course_id": course_id,
        "course_name": course_name,
        "enrollment_code": enrollment_code,
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


# Markdown 格式清理函數
# ── Flex Message Template APIs ──────────────────────────────────────

@csrf_exempt  
def api_get_flex_template(request):
    """
    API: 獲取 Flex Message 模板
    GET /line_bot/api/flex/<template_name>/
    """
    if request.method != "GET":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    # 從 URL 路徑獲取模板名稱
    path = request.path
    template_name = path.split('/')[-2] if path.endswith('/') else path.split('/')[-1]
    
    # 獲取模板
    template = get_flex_template(template_name)
    
    if not template:
        return JsonResponse({
            "error": "template_not_found",
            "message": f"模板 '{template_name}' 不存在",
            "available_templates": get_available_templates()
        }, status=404)
    
    return JsonResponse({
        "template_name": template_name,
        "template": template,
        "success": True
    })

@csrf_exempt
def api_send_flex_message(request):
    """
    API: 發送 Flex Message 到指定用戶
    POST /line_bot/api/send_flex/
    {
        "line_user_id": "用戶 LINE ID",
        "template_name": "模板名稱"
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)
    
    line_user_id = data.get("line_user_id", "").strip()
    template_name = data.get("template_name", "").strip()
    
    if not line_user_id or not template_name:
        return JsonResponse({"error": "missing_required_fields", "message": "需要提供 line_user_id 和 template_name"}, status=400)
    
    # 獲取模板
    template = get_flex_template(template_name)
    
    if not template:
        return JsonResponse({
            "error": "template_not_found",
            "message": f"模板 '{template_name}' 不存在",
            "available_templates": get_available_templates()
        }, status=404)
    
    try:
        # 發送 Flex Message
        flex_message = FlexSendMessage(
            alt_text=template.get("altText", "功能選單"),
            contents=template["contents"]
        )
        line_bot_api.push_message(line_user_id, flex_message)
        
        return JsonResponse({
            "success": True,
            "message": f"成功發送 {template_name} 模板到用戶 {line_user_id}",
            "template_name": template_name,
            "line_user_id": line_user_id
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "send_failed",
            "message": f"發送 Flex Message 失敗: {str(e)}"
        }, status=500)

@csrf_exempt
def api_list_flex_templates(request):
    """
    API: 列出所有可用的 Flex Message 模板
    GET /line_bot/api/flex/templates/
    """
    if request.method != "GET":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    templates = get_available_templates()
    
    template_info = []
    for template_name in templates:
        template = get_flex_template(template_name)
        if template:
            template_info.append({
                "name": template_name,
                "alt_text": template.get("altText", ""),
                "description": _get_template_description(template_name)
            })
    
    return JsonResponse({
        "success": True,
        "total_templates": len(template_info),
        "templates": template_info
    })

@csrf_exempt
def api_create_custom_carousel(request):
    """
    API: 創建自定義滾動式 Flex Message
    POST /line_bot/api/flex/custom_carousel/
    {
        "steps": [
            {
                "type": "STEP",
                "title": "STEP 1",
                "content": "第一步的說明內容",
                "description": "詳細描述",
                "button_text": "開始",
                "button_action": "message",
                "button_data": "開始操作",
                "bg_color": "#FFF4E6",
                "badge_color": "#FF6B35"
            }
        ],
        "title": "操作步驟",
        "alt_text": "步驟指南",
        "send_to_user": "LINE_USER_ID"  // 可選：直接發送給用戶
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)
    
    steps = data.get("steps", [])
    title = data.get("title", "操作步驟")
    alt_text = data.get("alt_text", "步驟指南")
    send_to_user = data.get("send_to_user", "")
    
    if not steps:
        return JsonResponse({"error": "missing_steps", "message": "需要提供步驟資料"}, status=400)
    
    try:
        # 創建自定義 carousel
        carousel_template = create_custom_carousel(steps, title, alt_text)
        
        response_data = {
            "success": True,
            "message": "自定義 Carousel 創建成功",
            "template": carousel_template,
            "steps_count": len(steps)
        }
        
        # 如果指定了用戶，直接發送
        if send_to_user:
            try:
                flex_message = FlexSendMessage(
                    alt_text=carousel_template.get("altText", alt_text),
                    contents=carousel_template["contents"]
                )
                line_bot_api.push_message(send_to_user, flex_message)
                response_data["sent_to_user"] = send_to_user
                response_data["message"] += f" 並已發送給用戶 {send_to_user}"
            except Exception as e:
                response_data["send_error"] = f"發送失敗: {str(e)}"
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "creation_failed",
            "message": f"創建 Carousel 失敗: {str(e)}"
        }, status=500)

@csrf_exempt
def api_get_template_categories(request):
    """
    API: 獲取模板分類資訊
    GET /line_bot/api/flex/categories/
    """
    if request.method != "GET":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    try:
        categories = get_template_categories()
        
        # 為每個分類添加詳細資訊
        detailed_categories = {}
        for category, templates in categories.items():
            template_details = []
            for template_name in templates:
                template = get_flex_template(template_name)
                if template:
                    template_details.append({
                        "name": template_name,
                        "alt_text": template.get("altText", ""),
                        "description": _get_template_description(template_name),
                        "type": "carousel" if "guide" in template_name else "bubble"
                    })
            
            detailed_categories[category] = {
                "templates": template_details,
                "count": len(template_details)
            }
        
        return JsonResponse({
            "success": True,
            "categories": detailed_categories,
            "total_categories": len(detailed_categories)
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "fetch_failed",
            "message": f"獲取分類資訊失敗: {str(e)}"
        }, status=500)

@csrf_exempt
def api_send_flex_batch(request):
    """
    API: 批量發送 Flex Message
    POST /line_bot/api/flex/batch_send/
    {
        "messages": [
            {
                "line_user_id": "USER_ID_1",
                "template_name": "main_menu"
            },
            {
                "line_user_id": "USER_ID_2", 
                "template_name": "course_creation_guide"
            }
        ]
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)
    
    messages = data.get("messages", [])
    
    if not messages:
        return JsonResponse({"error": "missing_messages", "message": "需要提供訊息列表"}, status=400)
    
    results = []
    success_count = 0
    failed_count = 0
    
    for msg in messages:
        line_user_id = msg.get("line_user_id", "").strip()
        template_name = msg.get("template_name", "").strip()
        
        if not line_user_id or not template_name:
            results.append({
                "line_user_id": line_user_id,
                "template_name": template_name,
                "success": False,
                "error": "missing_required_fields"
            })
            failed_count += 1
            continue
        
        # 獲取模板
        template = get_flex_template(template_name)
        if not template:
            results.append({
                "line_user_id": line_user_id,
                "template_name": template_name,
                "success": False,
                "error": "template_not_found"
            })
            failed_count += 1
            continue
        
        # 發送訊息
        try:
            flex_message = FlexSendMessage(
                alt_text=template.get("altText", "功能選單"),
                contents=template["contents"]
            )
            line_bot_api.push_message(line_user_id, flex_message)
            
            results.append({
                "line_user_id": line_user_id,
                "template_name": template_name,
                "success": True,
                "message": "發送成功"
            })
            success_count += 1
            
        except Exception as e:
            results.append({
                "line_user_id": line_user_id,
                "template_name": template_name,
                "success": False,
                "error": f"send_failed: {str(e)}"
            })
            failed_count += 1
    
    return JsonResponse({
        "success": True,
        "total_messages": len(messages),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    })

def _get_template_description(template_name):
    """獲取模板描述"""
    descriptions = {
        # 基本功能選單
        "main_menu": "主功能選單，包含所有主要功能入口",
        "course_menu": "課程管理功能選單，包含建立、查看、修改、刪除課程等功能",
        "homework_menu": "作業管理功能選單，包含新增、查看、修改、刪除作業等功能", 
        "calendar_menu": "行事曆管理功能選單，包含新增、查看、修改、刪除事件等功能",
        "notes_menu": "筆記管理功能選單，包含建立、查看、編輯、刪除筆記等功能",
        "account_menu": "帳戶設定功能選單，包含個人資料、Google綁定、通知設定等",
        
        # 滾動式指南
        "course_creation_guide": "課程建立步驟指南，滾動式展示完整建立流程",
        "homework_creation_guide": "作業建立步驟指南，滾動式展示作業新增流程", 
        "system_usage_guide": "系統使用指南，滾動式展示系統使用步驟"
    }
    return descriptions.get(template_name, "")

def clean_markdown_text(s):
    """清理 AI 回應中的 Markdown 格式，轉換成 Line 友好的純文字"""
    import re
    
    # 確保輸入是字符串
    if not isinstance(s, str):
        s = json.dumps(s, ensure_ascii=False) if s else ""
    
    # 移除三引號程式碼區塊（保留內容）
    s = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), s)
    
    # 移除粗體/斜體/底線
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)  # **粗體**
    s = re.sub(r'\*(.*?)\*', r'\1', s)      # *斜體*
    s = re.sub(r'__(.*?)__', r'\1', s)      # __底線粗體__
    s = re.sub(r'_(.*?)_', r'\1', s)        # _底線斜體_
    
    # 轉換連結 [text](url) → text (url)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', s)
    
    # 移除行內程式碼反引號
    s = re.sub(r'`([^`]+)`', r'\1', s)
    
    # 移除標題井字
    s = re.sub(r'^#{1,6}\s*', '', s, flags=re.MULTILINE)
    
    # 轉換表格管線為破折號
    s = re.sub(r'^\s*\|', '', s, flags=re.MULTILINE)    # 移除行開頭的 |
    s = re.sub(r'\|\s*$', '', s, flags=re.MULTILINE)    # 移除行結尾的 |
    s = re.sub(r'\s*\|\s*', ' - ', s)                   # 中間的 | 轉為 -
    
    # 將項目符號統一成「• 」
    s = re.sub(r'^\s*[-*•]\s+', '• ', s, flags=re.MULTILINE)
    
    # 清理多餘空白
    s = re.sub(r'\n{3,}', '\n\n', s)  # 多個換行變成雙換行
    s = s.strip()
    
    return s


# n8n 回應處理 API
@csrf_exempt
def api_n8n_response(request):
    """接收 n8n 處理後的 AI 回應並發送給用戶"""
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)

    # 必要參數檢查
    line_user_id = (data.get("lineUserId") or data.get("to") or "").strip()
    raw_text = data.get("text") or data.get("output") or data.get("answer") or ""
    
    if not line_user_id:
        return JsonResponse({"error": "missing lineUserId or to"}, status=400)
    
    if not raw_text:
        return JsonResponse({"error": "missing text/output/answer"}, status=400)

    try:
        # 清理 Markdown 格式
        cleaned_text = clean_markdown_text(raw_text)
        
        # 如果清理後的文字太長，進行截斷處理
        if len(cleaned_text) > 4500:  # Line 訊息長度限制大約 5000 字元
            cleaned_text = cleaned_text[:4500] + "...\n\n[訊息過長，已截斷顯示]"
        
        # 儲存Bot回應到資料庫
        try:
            ConversationMessage.objects.create(
                line_user_id=line_user_id,
                message_type="bot",
                content=cleaned_text,
                raw_data={
                    "original_length": len(str(raw_text)),
                    "cleaned_length": len(cleaned_text),
                    "source": "n8n"
                }
            )
        except Exception as e:
            print(f"儲存Bot回應失敗: {e}")
        
        # 發送給用戶
        line_bot_api.push_message(
            line_user_id, 
            TextSendMessage(text=cleaned_text)
        )
        
        return JsonResponse({
            "success": True,
            "original_length": len(str(raw_text)),
            "cleaned_length": len(cleaned_text),
            "sent_to": line_user_id
        })
        
    except Exception as e:
        print(f"處理 n8n 回應失敗: {e}")
        return JsonResponse({"error": str(e)}, status=500)


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


# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 統一 Flex 模板渲染 API - 專為 n8n 設計
# ════════════════════════════════════════════════════════════════════════════════════════════════════

@csrf_exempt
def render_flex(request):
    """
    統一的 Flex 模板渲染 API
    
    支援三種模式：
    1. 基本模板渲染 - 使用預定義模板
    2. 動態 Carousel 渲染 - 使用自定義數據
    3. 直接發送模式 - 渲染後直接發送給用戶
    
    POST /line/render-flex/
    {
        "template_name": "main_menu",           // 模板名稱
        "mode": "template",                     // 模式：template, carousel, send
        "payload": {...},                       // 自定義數據（僅 carousel 模式）
        "user_id": "Uxxx",                     // 用戶 ID（僅 send 模式）
        "send_type": "push"                     // 發送類型：push, reply（僅 send 模式）
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "只支援 POST 請求"}, status=405)
    
    try:
        data = json.loads(request.body)
        template_name = data.get('template_name')
        mode = data.get('mode', 'template')  # 預設為 template 模式
        payload = data.get('payload', {})
        user_id = data.get('user_id')
        send_type = data.get('send_type', 'push')
        
        if not template_name:
            return JsonResponse({"error": "缺少 template_name 參數"}, status=400)
        
        flex_message = None
        
                # ═══ 模式 1: 基本模板渲染 + 自動發送 ═══
        if mode == 'template':
            # 處理需要參數的模板
            if template_name in ['course_view', 'get_course_view', 'course_deletion_confirmation', 'course_deletion_confirmation_paginated']:
                courses = payload.get('courses', [])
                if not courses:
                    return JsonResponse({
                        "error": f"模板 {template_name} 需要 courses 參數",
                        "example": {
                            "courses": [
                                {"name": "課程名稱", "id": "課程ID"},
                                {"name": "另一個課程", "id": "另一個ID"}
                            ]
                        }
                    }, status=400)
                
                if template_name == 'course_deletion_confirmation_paginated':
                    page_size = payload.get('page_size', 8)
                    flex_message = get_flex_template(template_name, courses=courses, page_size=page_size)
                else:
                    flex_message = get_flex_template(template_name, courses=courses)
            elif template_name == 'student_homework_status':
                # 處理學生作業狀態模板
                homeworks = payload.get('homeworks', [])
                if not homeworks:
                    return JsonResponse({
                        "error": f"模板 {template_name} 需要 homeworks 參數",
                        "example": {
                            "homeworks": [
                                {
                                    "course_name": "課程名稱",
                                    "homework_title": "作業標題",
                                    "status": "TURNED_IN",
                                    "status_text": "✅ 已繳交",
                                    "is_late": False,
                                    "update_time": "2025-05-07"
                                }
                            ]
                        }
                    }, status=400)
                
                flex_message = get_flex_template(template_name, homeworks=homeworks)
            else:
                flex_message = get_flex_template(template_name)
            
            if not flex_message:
                return JsonResponse({
                    "error": f"找不到模板: {template_name}",
                    "available_templates": [
                        "main_menu", "course_menu", "homework_menu", 
                        "calendar_menu", "notes_menu", "account_menu",
                        "course_creation_guide", "homework_creation_guide", 
                        "system_usage_guide",
                        "course_view", "get_course_view",
                        "course_deletion_confirmation", "course_deletion_confirmation_paginated"
                    ]
                }, status=404)
            
            # 檢查 line_user_id 或 user_id
            line_user_id = data.get('line_user_id') or user_id
            
            # 如果有 line_user_id，自動發送到 LINE
            if line_user_id:
                try:
                    line_bot_api.push_message(
                        line_user_id,
                        FlexSendMessage(
                            alt_text=flex_message.get('altText', '功能選單'),
                            contents=flex_message['contents']
                        )
                    )
                    return JsonResponse({
                        "success": True,
                        "message": f"已成功發送 {template_name} 給用戶 {line_user_id}",
                        "template_name": template_name,
                        "mode": mode,
                        "line_user_id": line_user_id
                    })
                except Exception as send_error:
                    return JsonResponse({
                        "success": False,
                        "error": f"發送失敗: {str(send_error)}",
                        "template_name": template_name,
                        "line_user_id": line_user_id
                    }, status=500)
            else:
                # 沒有 line_user_id 時，只回傳模板內容（保持向後兼容）
                return JsonResponse({
                    "success": True,
                    "template_name": template_name,
                    "mode": mode,
                    "flex_message": flex_message,
                    "alt_text": flex_message.get('altText', '功能選單'),
                    "message": "模板渲染成功，但未發送（缺少 line_user_id）"
                })
        
        # ═══ 模式 2: 動態 Carousel 渲染 ═══
        elif mode == 'carousel':
            steps_data = payload.get('steps_data', [])
            title = payload.get('title', '操作步驟')
            alt_text = payload.get('alt_text', '步驟指南')
            
            if not steps_data:
                return JsonResponse({"error": "carousel 模式需要 steps_data"}, status=400)
            
            flex_message = create_custom_carousel(steps_data, title, alt_text)
        
        # ═══ 模式 3: 直接發送模式 ═══
        elif mode == 'send':
            # 檢查 line_user_id 或 user_id
            line_user_id = data.get('line_user_id') or user_id
            if not line_user_id:
                return JsonResponse({"error": "send 模式需要 line_user_id 或 user_id"}, status=400)
            
            # 先取得模板
            if template_name == 'custom_carousel':
                steps_data = payload.get('steps_data', [])
                title = payload.get('title', '操作步驟')
                alt_text = payload.get('alt_text', '步驟指南')
                flex_message = create_custom_carousel(steps_data, title, alt_text)
            elif template_name in ['course_deletion_confirmation', 'course_deletion_confirmation_paginated']:
                courses = payload.get('courses', [])
                if not courses:
                    return JsonResponse({
                        "error": f"模板 {template_name} 需要 courses 參數"
                    }, status=400)
                
                if template_name == 'course_deletion_confirmation_paginated':
                    page_size = payload.get('page_size', 8)
                    flex_message = get_flex_template(template_name, courses=courses, page_size=page_size)
                else:
                    flex_message = get_flex_template(template_name, courses=courses)
            elif template_name == 'student_homework_status':
                # 處理學生作業狀態模板
                homeworks = payload.get('homeworks', [])
                if not homeworks:
                    return JsonResponse({
                        "error": f"模板 {template_name} 需要 homeworks 參數"
                    }, status=400)
                
                flex_message = get_flex_template(template_name, homeworks=homeworks)
            else:
                flex_message = get_flex_template(template_name)
            
            if not flex_message:
                return JsonResponse({"error": f"找不到模板: {template_name}"}, status=404)
            
            # 發送訊息
            try:
                if send_type == 'push':
                    line_bot_api.push_message(
                        line_user_id,
                        FlexSendMessage(
                            alt_text=flex_message.get('altText', '功能選單'),
                            contents=flex_message['contents']
                        )
                    )
                    return JsonResponse({
                        "success": True,
                        "message": f"已推送 {template_name} 給用戶 {line_user_id}",
                        "template_name": template_name,
                        "mode": mode,
                        "send_type": send_type
                    })
                else:
                    return JsonResponse({"error": "reply 模式需要 reply_token"}, status=400)
            
            except Exception as send_error:
                return JsonResponse({
                    "success": False,
                    "error": f"發送失敗: {str(send_error)}",
                    "template_name": template_name,
                    "line_user_id": line_user_id
                }, status=500)
        
        else:
            return JsonResponse({
                "error": f"不支援的模式: {mode}",
                "supported_modes": ["template", "carousel", "send"]
            }, status=400)
        
        # 返回渲染結果
        return JsonResponse({
            "success": True,
            "template_name": template_name,
            "mode": mode,
            "flex_message": flex_message,
            "alt_text": flex_message.get('altText', '功能選單')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "無效的 JSON 格式"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"處理請求時發生錯誤: {str(e)}"}, status=500)


# ════════════════════════════════════════════════════════════════════════════════════════════════════
# 自動通知缺交學生 API
# ════════════════════════════════════════════════════════════════════════════════════════════════════

@csrf_exempt
def api_notify_unsubmitted_students(request):
    """
    自動通知缺交學生 API
    從資料庫暫存讀取缺交學生資料並發送通知
    
    POST /line_bot/api/notify_unsubmitted_students/
    {
        "line_user_id": "教師的LINE用戶ID",
        "course_id": "Google Classroom課程ID", 
        "coursework_id": "Google Classroom作業ID"
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)
    
    line_user_id = (data.get("line_user_id") or "").strip()
    course_id = (data.get("course_id") or "").strip()
    coursework_id = (data.get("coursework_id") or "").strip()
    
    if not line_user_id or not course_id or not coursework_id:
        return JsonResponse({
            "error": "missing_required_fields",
            "message": "需要提供 line_user_id, course_id, coursework_id",
            "required": ["line_user_id", "course_id", "coursework_id"]
        }, status=400)
    
    try:
        # 調用通知功能
        from line_bot.utils import notify_unsubmitted_students_from_cache
        
        result = notify_unsubmitted_students_from_cache(
            teacher_line_user_id=line_user_id,
            course_id=course_id,
            coursework_id=coursework_id
        )
        
        # 檢查是否有錯誤
        if "error" in result:
            return JsonResponse({
                "success": False,
                "error": result["error"],
                "message": result.get("message", ""),
                "details": result.get("details", "")
            }, status=400)
        
        # 成功執行通知
        return JsonResponse({
            "success": True,
            "message": "自動通知已執行完成",
            "results": {
                "total_students": result["total_students"],
                "line_notified": result["line_notified"],
                "email_notified": result["email_notified"],
                "failed": result["failed"]
            },
            "summary": f"成功通知 {result['line_notified'] + result['email_notified']}/{result['total_students']} 位缺交學生"
        })
        
    except Exception as e:
        print(f"自動通知API失敗: {e}")
        return JsonResponse({
            "success": False,
            "error": "notification_failed",
            "message": "自動通知功能發生錯誤",
            "details": str(e)
        }, status=500)