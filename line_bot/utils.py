import os, hashlib
from linebot import LineBotApi
from linebot.models import FlexSendMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from googleapiclient.discovery import build
from user.models import LineProfile
from user.utils import get_valid_google_credentials

# LINE Bot API 設定
CHANNEL_TOKEN = os.getenv("CHANNEL_TOKEN")
line_bot_api = LineBotApi(CHANNEL_TOKEN)


def hash_code(plain_code: str) -> str:
    return hashlib.sha256(plain_code.encode("utf-8")).hexdigest()


def reply_text(reply_token: str, text: str) -> None:
    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    except Exception as e:
        print(f"LINE reply 失敗: {e}")


def push_to_group(group_id: str, text: str) -> bool:
    try:
        line_bot_api.push_message(group_id, TextSendMessage(text=text))
        return True
    except Exception as e:
        print(f"推播到群組失敗: {e}")
        return False

def send_course_created_message(line_user_id: str, course_name: str, gc_course_id: str, enrollment_code: str, alternate_link: str = None):
    """
    發送課程創建成功的Flex Message
    """
    
    # 建立按鈕
    buttons = []
    if alternate_link:
        buttons.append({
            "type": "button",
            "style": "primary",
            "action": {
                "type": "uri",
                "label": "在 Google Classroom 中開啟",
                "uri": alternate_link
            }
        })
    
    # 如果沒有連結，可以放一個返回主選單的按鈕
    buttons.append({
        "type": "button",
        "style": "secondary",
        "margin": "sm",
        "action": {
            "type": "message",
            "label": "返回主選單",
            "text": "主選單"
        }
    })

    flex_message = {
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
                    "backgroundColor": "#2196F3",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "md",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🎓",
                                    "size": "3xl",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "課程創建成功！",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FFFFFF",
                                    "align": "center",
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": f"課程：{course_name}",
                                    "size": "md",
                                    "color": "#E3F2FD",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                # 課程資訊卡片
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
                                # 課程ID
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
                                                    "text": "🆔",
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
                                                    "text": "課程ID",
                                                    "size": "xs",
                                                    "color": "#6C757D",
                                                    "weight": "bold"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": gc_course_id,
                                                    "size": "sm",
                                                    "color": "#2196F3",
                                                    "weight": "bold"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                # 註冊碼
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
                                                    "text": "🔑",
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
                                                    "text": "註冊碼",
                                                    "size": "xs",
                                                    "color": "#6C757D",
                                                    "weight": "bold"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": enrollment_code,
                                                    "size": "sm",
                                                    "color": "#2196F3",
                                                    "weight": "bold"
                                                }
                                            ]
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
                # 操作按鈕
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "spacing": "md",
                    "contents": buttons
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="課程創建成功", contents=flex_message)
        )
        # print("課程創建成功訊息已註解")
        return True
    except Exception as e:
        print(f"發送課程創建消息失敗: {e}")
        return False

def send_homework_created_message(line_user_id: str, homework_title: str, course_name: str, due_date: str, gc_course_id: str, alternate_link: str = None, homework_description: str = ""):
    """
    發送作業創建成功的Flex Message
    """
    
    # 設定連結，優先使用 alternate_link，否則使用課程連結
    assignment_link = alternate_link if alternate_link else f"https://classroom.google.com/c/{gc_course_id}"
    
    # 處理作業描述，如果為空則顯示預設訊息
    if not homework_description or homework_description.strip() == "":
        homework_description = "請依照老師的指示完成作業"
    
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "新作業通知",
                    "weight": "bold",
                    "color": "#ffffff",
                    "size": "md"
                },
                {
                    "type": "text",
                    "text": course_name,
                    "color": "#ffffff",
                    "weight": "bold",
                    "size": "md",
                    "align": "end"
                }
            ],
            "backgroundColor": "#0367D3"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "NEW",
                            "size": "xs",
                            "align": "center",
                            "color": "#ffffff",
                            "gravity": "center"
                        }
                    ],
                    "position": "absolute",
                    "flex": 0,
                    "width": "48px",
                    "height": "25px",
                    "backgroundColor": "#EC3D44",
                    "cornerRadius": "100px",
                    "paddingAll": "2px",
                    "paddingStart": "4px",
                    "paddingEnd": "4px",
                    "offsetTop": "18px",
                    "offsetStart": "18px"
                },
                {
                    "type": "text",
                    "text": "📝",
                    "margin": "none",
                    "size": "3xl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": homework_title,
                    "weight": "bold",
                    "size": "xl",
                    "margin": "md",
                    "align": "center"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "separator",
                                    "margin": "lg"
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "截止日期",
                            "size": "sm",
                            "align": "center",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "separator",
                                    "margin": "lg"
                                }
                            ]
                        }
                    ],
                    "margin": "xxl"
                },
                {
                    "type": "text",
                    "text": f"{due_date} 23:59",
                    "color": "#ff5551",
                    "size": "sm",
                    "weight": "bold",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "separator",
                                    "margin": "lg"
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "作業說明",
                            "size": "sm",
                            "align": "center",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "separator",
                                    "margin": "lg"
                                }
                            ]
                        }
                    ],
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": homework_description,
                            "size": "sm",
                            "color": "#555555",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "前往Google Classroom",
                            "action": {
                                "type": "uri",
                                "label": "開啟作業",
                                "uri": assignment_link
                            },
                            "align": "center",
                            "gravity": "center",
                            "color": "#ffffff",
                            "weight": "bold"
                        }
                    ],
                    "backgroundColor": "#0367D3",
                    "cornerRadius": "md",
                    "margin": "xxl",
                    "paddingTop": "xl",
                    "paddingBottom": "xl"
                }
            ]
        },
        "styles": {
            "footer": {
                "separator": True
            }
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="作業創建成功", contents=flex_message)
        )
        # print("作業創建成功訊息已註解")
        return True
    except Exception as e:
        print(f"發送作業創建消息失敗: {e}")
        return False

def send_quick_reply(line_user_id: str):
    """
    發送 Quick Reply 按鈕訊息
    """
    message = TextSendMessage(
        text=" ",  # 使用全形空格，視覺上幾乎看不到
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="查看班級", text="查看我的班級")),
                QuickReplyButton(action=MessageAction(label="新增作業", text="我要新增作業")),
                QuickReplyButton(action=MessageAction(label="課堂提問", text="我要提問")),
                QuickReplyButton(action=MessageAction(label="建立課程", text="我要建立一個班級")),
            ]
        )
    )

    try:
        line_bot_api.push_message(line_user_id, message)
        # print("Quick Reply 訊息已註解")
        return True
    except Exception as e:
        print(f"發送 Quick Reply 消息失敗: {e}")
        return False

def send_courses_list(line_user_id: str):
    """
    從 Google Classroom 獲取課程列表並發送 Flex Message
    """
    try:
        # 獲取用戶資料
        profile = LineProfile.objects.get(line_user_id=line_user_id)
        
        # 獲取有效的 Google 憑證（自動處理刷新）
        try:
            creds = get_valid_google_credentials(profile)
        except Exception as e:
            print(f"Google 憑證獲取失敗 (用戶: {line_user_id}): {str(e)}")
            return False
        
        # 建立 Google Classroom service
        service = build("classroom", "v1", credentials=creds, cache_discovery=False)
        
        # 獲取課程列表
        courses_response = service.courses().list(
            courseStates=["ACTIVE"],
            pageSize=10
        ).execute()
        
        courses = courses_response.get("courses", [])
        
        if not courses:
            # 沒有課程時的 Flex Message
            flex_message = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "backgroundColor": "#FFFFFF",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📚",
                            "size": "3xl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "目前沒有課程",
                            "size": "lg",
                            "weight": "bold",
                            "align": "center",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "你還沒有建立任何課程，或尚未加入任何課程。",
                            "size": "sm",
                            "color": "#666666",
                            "align": "center",
                            "wrap": True
                        }
                    ]
                }
            }
        else:
            # 有課程時的 Flex Message
            course_contents = []
            
            for course in courses:
                course_content = {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "paddingAll": "16px",
                    "backgroundColor": "#F8F9FA",
                    "cornerRadius": "12px",
                    "margin": "sm",
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
                                    "text": "🎓",
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
                                    "text": course.get("name", "未命名課程"),
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#2196F3"
                                },
                                {
                                    "type": "text",
                                    "text": course.get("section", "無描述"),
                                    "size": "sm",
                                    "color": "#666666",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": f"課程ID: {course.get('id', 'N/A')}",
                                    "size": "xs",
                                    "color": "#999999"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 0,
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "link",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "選擇",
                                        "data": f"course:{course.get('id', '')}",
                                        "displayText": f"{course.get('id', '')} {course.get('name', '未命名課程')}"
                                    }
                                }
                            ]
                        }
                    ]
                }
                course_contents.append(course_content)
            
            flex_message = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "0px",
                    "backgroundColor": "#FFFFFF",
                    "contents": [
                        # 頂部標題區域
                        {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "24px",
                            "paddingBottom": "16px",
                            "backgroundColor": "#2196F3",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📚",
                                    "size": "3xl",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "你的課程列表",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FFFFFF",
                                    "align": "center",
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": f"共找到 {len(courses)} 個課程",
                                    "size": "sm",
                                    "color": "#E3F2FD",
                                    "align": "center"
                                }
                            ]
                        },
                        # 課程列表
                        {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "16px",
                            "contents": course_contents
                        }
                    ]
                }
            }
        
        # 發送 Flex Message
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="課程列表", contents=flex_message)
        )
        # print("課程列表訊息已註解")
        return True
        
    except LineProfile.DoesNotExist:
        print(f"用戶 {line_user_id} 不存在")
        return False
    except Exception as e:
        print(f"獲取課程列表失敗: {e}")
        return False 

def send_create_course_guide(line_user_id: str):
    """
    發送建立課程的指引訊息
    """
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "0px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                # 頂部標題區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "paddingBottom": "16px",
                    "backgroundColor": "#4CAF50",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🎓",
                            "size": "3xl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "建立新課程",
                            "size": "xl",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "align": "center",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": "在 Google Classroom 建立新課程",
                            "size": "sm",
                            "color": "#E8F5E8",
                            "align": "center"
                        }
                    ]
                },
                # 內容區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "請按照以下格式輸入：",
                            "size": "md",
                            "weight": "bold",
                            "color": "#333333",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "建立課程 課程名稱",
                                    "size": "sm",
                                    "color": "#4CAF50",
                                    "weight": "bold",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "例如：建立課程 程式設計概論",
                                    "size": "xs",
                                    "color": "#666666",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "💡 提示：課程會自動在 Google Classroom 中建立",
                            "size": "xs",
                            "color": "#4CAF50",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="建立課程指引", contents=flex_message)
        )
        # print("建立課程指引訊息已註解")
        return True
    except Exception as e:
        print(f"發送建立課程指引失敗: {e}")
        return False

def send_add_homework_guide(line_user_id: str):
    """
    發送新增作業的指引訊息
    """
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "0px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                # 頂部標題區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "paddingBottom": "16px",
                    "backgroundColor": "#FF6B35",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📚",
                            "size": "3xl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "新增作業",
                            "size": "xl",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "align": "center",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": "為指定課程建立新作業",
                            "size": "sm",
                            "color": "#FFE8E0",
                            "align": "center"
                        }
                    ]
                },
                # 內容區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "請按照以下格式輸入：",
                            "size": "md",
                            "weight": "bold",
                            "color": "#333333",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "新增作業 課程ID 作業標題 到期日期",
                                    "size": "sm",
                                    "color": "#FF6B35",
                                    "weight": "bold",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "例如：新增作業 1234567890 期末報告 2024-01-15",
                                    "size": "xs",
                                    "color": "#666666",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "💡 提示：可以先點擊「查看班級」獲取課程ID",
                            "size": "xs",
                            "color": "#FF6B35",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="新增作業指引", contents=flex_message)
        )
        # print("新增作業指引訊息已註解")
        return True
    except Exception as e:
        print(f"發送新增作業指引失敗: {e}")
        return False

def send_ask_question_guide(line_user_id: str):
    """
    發送課堂提問的指引訊息
    """
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "0px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                # 頂部標題區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "paddingBottom": "16px",
                    "backgroundColor": "#9C27B0",
                    "contents": [
                        {
                            "type": "text",
                            "text": "❓",
                            "size": "3xl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "課堂提問",
                            "size": "xl",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "align": "center",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": "有任何問題都可以詢問",
                            "size": "sm",
                            "color": "#F3E5F5",
                            "align": "center"
                        }
                    ]
                },
                # 內容區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "請直接輸入你的問題：",
                            "size": "md",
                            "weight": "bold",
                            "color": "#333333",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "例如：如何建立新的課程？",
                                    "size": "sm",
                                    "color": "#9C27B0",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "例如：如何新增作業？",
                                    "size": "sm",
                                    "color": "#9C27B0",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "例如：如何使用這個系統？",
                                    "size": "sm",
                                    "color": "#9C27B0",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": "💡 提示：AI 會根據你的問題提供協助",
                            "size": "xs",
                            "color": "#9C27B0",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="課堂提問指引", contents=flex_message)
        )
        # print("課堂提問指引訊息已註解")
        return True
    except Exception as e:
        print(f"發送課堂提問指引失敗: {e}")
        return False

def send_course_binding_success_message(group_id: str, course_id: str, bound_by_line_user_id: str = ""):
    """
    發送課程綁定成功的Flex Message到群組
    """
    try:
        # 從本地數據庫獲取課程信息
        from course.models import Course
        try:
            local_course = Course.objects.get(gc_course_id=course_id)
            course_name = local_course.name
            enrollment_code = local_course.enrollment_code
            course_description = local_course.description or f"歡迎加入 {course_name}！"
            section_info = local_course.section or ""
            try:
                teacher_name = local_course.owner.name or "老師"
            except:
                teacher_name = "老師"
        except Course.DoesNotExist:
            # 如果本地沒有，使用預設信息
            course_name = f"課程 {course_id}"
            enrollment_code = ""
            course_description = "歡迎加入這個課程！"
            section_info = ""
            teacher_name = "老師"
        
        # 獲取綁定者名稱
        bound_by_name = "系統管理員"
        if bound_by_line_user_id:
            try:
                from user.models import LineProfile
                bound_by_profile = LineProfile.objects.get(line_user_id=bound_by_line_user_id)
                bound_by_name = bound_by_profile.name or bound_by_profile.line_user_id
            except LineProfile.DoesNotExist:
                bound_by_name = "未知用戶"
        
        # 生成加入課程的連結 - 強制使用邀請碼，確保可被直接邀請入班
        join_link = f"https://classroom.google.com/c/{course_id}?cjc={enrollment_code}"
        
        flex_message = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "群組綁定成功",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": "🎓",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "end"
                    }
                ],
                "backgroundColor": "#4CAF50"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "NEW",
                                "size": "xs",
                                "align": "center",
                                "color": "#ffffff",
                                "gravity": "center"
                            }
                        ],
                        "position": "absolute",
                        "flex": 0,
                        "width": "48px",
                        "height": "25px",
                        "backgroundColor": "#FF5722",
                        "cornerRadius": "100px",
                        "paddingAll": "2px",
                        "paddingStart": "4px",
                        "paddingEnd": "4px",
                        "offsetTop": "18px",
                        "offsetStart": "18px"
                    },
                    {
                        "type": "text",
                        "text": "🎉",
                        "margin": "none",
                        "size": "3xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": course_name,
                        "weight": "bold",
                        "size": "xl",
                        "margin": "md",
                        "align": "center",
                        "wrap": True
                    }
                ]
            }
        }
        
        # 如果有班級資訊，顯示出來
        if section_info:
            flex_message["body"]["contents"].append({
                "type": "text",
                "text": section_info,
                "size": "sm",
                "color": "#666666",
                "align": "center",
                "margin": "sm",
                "wrap": True
            })
        
        # 添加課程資訊分隔線和課程ID
        flex_message["body"]["contents"].extend([
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "margin": "lg"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "課程資訊",
                        "size": "sm",
                        "align": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "margin": "lg"
                            }
                        ]
                    }
                ],
                "margin": "xxl"
            },
            {
                "type": "text",
                "text": f"課程名稱：{course_name}",
                "color": "#4CAF50",
                "size": "sm",
                "weight": "bold",
                "align": "center",
                "margin": "md"
            }
        ])
        
        # 添加入班資訊分隔線和註冊碼
        flex_message["body"]["contents"].extend([
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "margin": "lg"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "入班資訊",
                        "size": "sm",
                        "align": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "margin": "lg"
                            }
                        ]
                    }
                ],
                "margin": "xxl"
            },
            {
                "type": "text",
                "text": f"註冊碼：{enrollment_code}",
                "color": "#FF9800",
                "size": "sm",
                "weight": "bold",
                "align": "center",
                "margin": "md"
            },
            {
                "type": "text",
                "text": "學生可使用此註冊碼加入課程",
                "color": "#666666",
                "size": "xs",
                "align": "center",
                "margin": "xs"
            }
        ])
        
        # 添加前往按鈕
        flex_message["body"]["contents"].extend([
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "前往Google Classroom",
                        "action": {
                            "type": "uri",
                            "label": "加入課程",
                            "uri": join_link
                        },
                        "align": "center",
                        "gravity": "center",
                        "color": "#ffffff",
                        "weight": "bold"
                    }
                ],
                "backgroundColor": "#4CAF50",
                "cornerRadius": "md",
                "margin": "xxl",
                "paddingTop": "xl",
                "paddingBottom": "xl"
            },
            {
                "type": "text",
                "text": f"綁定者：{bound_by_name}",
                "color": "#999999",
                "size": "xs",
                "align": "center",
                "margin": "md"
            }
        ])
        
        # 加入 styles
        flex_message["styles"] = {
            "footer": {
                "separator": True
            }
        }
        
        line_bot_api.push_message(
            group_id,
            FlexSendMessage(alt_text="課程綁定成功", contents=flex_message)
        )
        return True
        
    except Exception as e:
        print(f"發送課程綁定成功訊息失敗: {e}")
        return False

def send_multiple_homework_created_message(line_user_id: str, homework_title: str, due_date: str, results: list, errors: list = None):
    """
    發送多個作業創建成功的Flex Message
    """
    if errors is None:
        errors = []
    
    success_count = len(results)
    total_count = success_count + len(errors)
    
    # 構建成功課程的內容
    course_contents = []
    for result in results:
        
        # 為每個成功的作業建立按鈕
        buttons = []
        if result.get("alternate_link"):
            buttons.append({
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "查看作業",
                    "uri": result.get("alternate_link")
                }
            })

        course_content = {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "paddingAll": "16px",
            "backgroundColor": "#F8F9FA",
            "cornerRadius": "12px",
            "margin": "sm",
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
                            "text": "✅",
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
                            "text": result["course_name"],
                            "size": "md",
                            "weight": "bold",
                            "color": "#4CAF50"
                        },
                        {
                            "type": "text",
                            "text": f"課程ID: {result['course_id']}",
                            "size": "xs",
                            "color": "#666666"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "flex": 0,
                    "contents": buttons
                }
            ]
        }
        course_contents.append(course_content)
    
    # 構建失敗課程的內容
    error_contents = []
    for error in errors:
        error_content = {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "paddingAll": "16px",
            "backgroundColor": "#FFF3E0",
            "cornerRadius": "12px",
            "margin": "sm",
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
                            "text": "❌",
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
                            "text": f"課程 {error['course_id']}",
                            "size": "md",
                            "weight": "bold",
                            "color": "#FF9800"
                        },
                        {
                            "type": "text",
                            "text": "創建失敗",
                            "size": "xs",
                            "color": "#666666"
                        }
                    ]
                }
            ]
        }
        error_contents.append(error_content)
    
    # 構建Flex Message
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "0px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                # 頂部標題區域
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "32px",
                    "paddingBottom": "24px",
                    "backgroundColor": "#FF6B35",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "md",
                            "alignItems": "center",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📚",
                                    "size": "3xl",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "作業創建完成！",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FFFFFF",
                                    "align": "center",
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": f"成功創建：{success_count}/{total_count} 個課程",
                                    "size": "md",
                                    "color": "#FFE8E0",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                # 作業資訊卡片
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
                                # 作業標題
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
                                                    "text": "📝",
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
                                                    "text": "作業標題",
                                                    "size": "xs",
                                                    "color": "#6C757D",
                                                    "weight": "bold"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": homework_title,
                                                    "size": "sm",
                                                    "color": "#FF6B35",
                                                    "weight": "bold"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                # 到期時間
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
                                                    "text": "⏰",
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
                                                    "text": "到期時間",
                                                    "size": "xs",
                                                    "color": "#6C757D",
                                                    "weight": "bold"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": f"{due_date} 23:59",
                                                    "size": "sm",
                                                    "color": "#FF6B35",
                                                    "weight": "bold"
                                                }
                                            ]
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
                # 課程列表
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📋 課程列表",
                            "size": "md",
                            "weight": "bold",
                            "color": "#343A40",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": course_contents + error_contents
                        }
                    ]
                },
                # 操作按鈕
                {
                    "type": "box",
                    "layout": "vertical",
                    "paddingAll": "24px",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "action": {
                                        "type": "uri",
                                        "label": "前往 Google Classroom",
                                        "uri": "https://classroom.google.com"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="多個作業創建成功", contents=flex_message)
        )
        # print("多個作業創建成功訊息已註解")
        return True
    except Exception as e:
        print(f"發送多個作業創建消息失敗: {e}")
        return False
