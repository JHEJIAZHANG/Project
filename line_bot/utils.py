# line_bot/utils.py
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
    
    # 設定課程連結，優先使用 alternate_link，否則使用編碼後的 classroom 連結
    from .utils_encoding import create_google_classroom_course_url
    course_link = alternate_link if alternate_link else create_google_classroom_course_url(gc_course_id)

    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "課程創建成功!",
                    "weight": "bold",
                    "color": "#ffffff",
                    "size": "md",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "🎉",
                    "margin": "lg",
                    "size": "3xl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": course_name,
                    "weight": "bold",
                    "size": "xl",
                    "margin": "lg",
                    "align": "center",
                    "color": "#ffffff"
                }
            ],
            "backgroundColor": "#0367D3"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "size": "sm",
                    "align": "center",
                    "weight": "bold",
                    "text": "課程代碼"
                },
                {
                    "type": "text",
                    "text": enrollment_code,
                    "size": "md",
                    "color": "#0367D3",
                    "margin": "md",
                    "weight": "bold",
                    "align": "center",
                    "gravity": "center"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "align": "center",
                            "weight": "bold",
                            "text": "綁定課程群組",
                            "color": "#ffffff",
                            "gravity": "center"
                        }
                    ],
                    "paddingBottom": "xl",
                    "margin": "xxl",
                    "backgroundColor": "#0367D3",
                    "cornerRadius": "md",
                    "paddingTop": "xl",
                    "action": {
                        "type": "message",
                        "label": "action",
                        "text": f"綁定{course_name}"
                    }
                },
                {
                    "type": "text",
                    "text": "點擊取得綁定序號",
                    "size": "xs",
                    "align": "center",
                    "margin": "md",
                    "color": "#aaaaaa"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "image",
                    "url": "https://img.icons8.com/?size=100&id=31057&format=png&color=000000",
                    "flex": 2,
                    "gravity": "center"
                },
                {
                    "type": "text",
                    "text": "Google Classroom",
                    "color": "#999999",
                    "weight": "bold",
                    "gravity": "center",
                    "size": "xs",
                    "flex": 19,
                    "margin": "sm"
                },
                {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/service-notifier/footer_go_btn.png",
                    "flex": 1,
                    "gravity": "center",
                    "size": "xxs"
                }
            ],
            "flex": 1,
            "spacing": "md",
            "margin": "md",
            "action": {
                "type": "uri",
                "label": "action",
                "uri": course_link
            }
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
    
    # 設定連結，優先使用 alternate_link，否則使用編碼後的課程連結
    from .utils_encoding import create_google_classroom_course_url
    assignment_link = alternate_link if alternate_link else create_google_classroom_course_url(gc_course_id)
    
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
        
        # 生成加入課程的連結 - 使用Base64編碼的課程ID和邀請碼
        from .utils_encoding import create_google_classroom_course_url
        join_link = f"{create_google_classroom_course_url(course_id)}?cjc={enrollment_code}"
        
        flex_message = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "群組綁定成功",
                        "size": "md",
                        "align": "center",
                        "weight": "bold",
                        "color": "#1DB446"
                    },
                    {
                        "type": "image",
                        "url": "https://img.icons8.com/?size=100&id=63262&format=png&color=000000",
                        "size": "xs",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": course_name,
                        "weight": "bold",
                        "align": "center",
                        "size": "xl",
                        "wrap": True,
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": f"課程代碼：{enrollment_code}",
                        "size": "sm",
                        "weight": "bold",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "加入課程",
                                "color": "#FFFFFF",
                                "weight": "bold",
                                "align": "center",
                                "gravity": "center",
                                "size": "lg"
                            }
                        ],
                        "margin": "xxl",
                        "backgroundColor": "#1DB446",
                        "cornerRadius": "md",
                        "paddingTop": "xl",
                        "paddingBottom": "xl",
                        "action": {
                            "type": "uri",
                            "label": "action",
                            "uri": join_link
                        }
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"綁定者 {bound_by_name}",
                        "size": "sm",
                        "align": "center",
                        "color": "#999999"
                    }
                ]
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

def send_calendar_created_message(line_user_id: str, event_title: str, start_time: str, end_time: str, 
                                  location: str = "", description: str = "", attendees: str = ""):
    """
    發送創建行事曆成功的Flex Message
    """
    
    # 處理描述內容，限制長度避免訊息過長
    display_description = description
    if len(display_description) > 50:
        display_description = display_description[:50] + "..."
    if not display_description:
        display_description = "無備註內容"
    
    # 處理地點
    if not location:
        location = "未設定地點"
    
    # 處理參與者
    if not attendees:
        attendees = "無參與者"
    
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "新行程",
                    "color": "#0367D3",
                    "weight": "bold",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": event_title,
                    "weight": "bold",
                    "size": "xl",
                    "color": "#222222",
                    "wrap": True,
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": f"{start_time} - {end_time}",
                    "size": "sm",
                    "margin": "md",
                    "color": "#999999",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": display_description,
                    "margin": "xl",
                    "color": "#222222",
                    "size": "sm",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "地點",
                            "color": "#989898",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": location,
                            "flex": 8,
                            "size": "sm",
                            "color": "#222222",
                            "wrap": True
                        }
                    ],
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "參與者",
                            "color": "#989898",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": attendees,
                            "flex": 8,
                            "size": "sm",
                            "color": "#0E71EB",
                            "wrap": True
                        }
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "NEW",
                            "size": "xs",
                            "color": "#ffffff",
                            "align": "center",
                            "gravity": "center"
                        }
                    ],
                    "position": "absolute",
                    "flex": 0,
                    "width": "48px",
                    "height": "25px",
                    "backgroundColor": "#EC3D44",
                    "cornerRadius": "100px",
                    "offsetTop": "18px",
                    "offsetEnd": "18px",
                    "paddingAll": "2px",
                    "paddingStart": "4px",
                    "paddingEnd": "4px"
                }
            ]
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="行事曆創建成功", contents=flex_message)
        )
        return True
    except Exception as e:
        print(f"發送行事曆創建消息失敗: {e}")
        return False

def send_note_created_message(line_user_id: str, note_id: int, text: str = "", image_url: str = "", 
                              course_name: str = "", note_type: str = "", tags: str = "", 
                              priority: str = "", classified_by: str = "none", created_at: str = ""):
    """
    發送筆記創建成功的Flex Message
    """
    
    # 處理文字內容，限制長度避免訊息過長
    display_text = text
    if len(display_text) > 100:
        display_text = display_text[:100] + "..."
    if not display_text:
        display_text = "無文字內容"
    
    # 處理課程資訊
    if not course_name:
        course_name = "未分類課程"
    
    # 處理分類標籤
    if not note_type:
        note_type = "一般筆記"
    
    # 處理標籤
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # 處理優先級
    priority_emoji = {
        "高": "🔴",
        "中": "🟡", 
        "低": "🟢",
        "緊急": "🚨"
    }
    priority_display = priority_emoji.get(priority, "⚪") + " " + (priority if priority else "普通")
    
    # 分類方式顯示
    classified_display = {
        "time": "⏰ 依時間自動分類",
        "name": "📚 依課程名稱分類", 
        "none": "📝 手動分類"
    }
    
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "筆記創建成功",
                    "weight": "bold",
                    "color": "#ffffff",
                    "size": "md"
                },
                {
                    "type": "text",
                    "text": "📝",
                    "color": "#ffffff",
                    "size": "lg",
                    "align": "end"
                }
            ],
            "backgroundColor": "#9C27B0"
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
                    "backgroundColor": "#4CAF50",
                    "cornerRadius": "100px",
                    "paddingAll": "2px",
                    "paddingStart": "4px",
                    "paddingEnd": "4px",
                    "offsetTop": "18px",
                    "offsetStart": "18px"
                },
                {
                    "type": "text",
                    "text": "✨",
                    "margin": "none",
                    "size": "3xl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": note_type,
                    "weight": "bold",
                    "size": "xl",
                    "margin": "md",
                    "align": "center",
                    "color": "#9C27B0"
                },
                # 分隔線 - 筆記內容
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
                            "text": "筆記內容",
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
                    "paddingAll": "16px",
                    "backgroundColor": "#F8F9FA",
                    "cornerRadius": "12px",
                    "contents": [
                        {
                            "type": "text",
                            "text": display_text,
                            "size": "sm",
                            "color": "#333333",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
    }
    
    # 如果有圖片，添加圖片區塊
    if image_url:
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
                        "text": "圖片內容",
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
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "margin": "md",
                "action": {
                    "type": "uri",
                    "uri": image_url
                }
            }
        ])
    
    # 添加詳細資訊區塊
    info_contents = []
    
    # 課程資訊
    info_contents.append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "md",
        "paddingAll": "12px",
        "backgroundColor": "#E3F2FD",
        "cornerRadius": "8px",
        "margin": "sm",
        "contents": [
            {
                "type": "text",
                "text": "📚",
                "size": "md",
                "flex": 0
            },
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {
                        "type": "text",
                        "text": "課程",
                        "size": "xs",
                        "color": "#666666"
                    },
                    {
                        "type": "text",
                        "text": course_name,
                        "size": "sm",
                        "weight": "bold",
                        "color": "#1976D2"
                    }
                ]
            }
        ]
    })
    
    # 優先級資訊
    info_contents.append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "md", 
        "paddingAll": "12px",
        "backgroundColor": "#FFF3E0",
        "cornerRadius": "8px",
        "margin": "sm",
        "contents": [
            {
                "type": "text",
                "text": "🎯",
                "size": "md",
                "flex": 0
            },
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {
                        "type": "text",
                        "text": "優先級",
                        "size": "xs",
                        "color": "#666666"
                    },
                    {
                        "type": "text",
                        "text": priority_display,
                        "size": "sm",
                        "weight": "bold",
                        "color": "#F57C00"
                    }
                ]
            }
        ]
    })
    
    # 分類方式
    info_contents.append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "md",
        "paddingAll": "12px", 
        "backgroundColor": "#E8F5E8",
        "cornerRadius": "8px",
        "margin": "sm",
        "contents": [
            {
                "type": "text",
                "text": "🏷️",
                "size": "md",
                "flex": 0
            },
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {
                        "type": "text",
                        "text": "分類方式",
                        "size": "xs",
                        "color": "#666666"
                    },
                    {
                        "type": "text",
                        "text": classified_display.get(classified_by, "📝 手動分類"),
                        "size": "sm",
                        "weight": "bold",
                        "color": "#388E3C"
                    }
                ]
            }
        ]
    })
    
    # 如果有標籤，顯示標籤
    if tag_list:
        tags_display = " ".join([f"#{tag}" for tag in tag_list[:3]])  # 最多顯示3個標籤
        if len(tag_list) > 3:
            tags_display += f" +{len(tag_list)-3}"
            
        info_contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "paddingAll": "12px",
            "backgroundColor": "#FCE4EC",
            "cornerRadius": "8px", 
            "margin": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "🏷️",
                    "size": "md",
                    "flex": 0
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "flex": 1,
                    "contents": [
                        {
                            "type": "text",
                            "text": "標籤",
                            "size": "xs",
                            "color": "#666666"
                        },
                        {
                            "type": "text",
                            "text": tags_display,
                            "size": "sm",
                            "weight": "bold",
                            "color": "#C2185B",
                            "wrap": True
                        }
                    ]
                }
            ]
        })
    
    # 添加詳細資訊區塊到訊息
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
                    "text": "筆記資訊",
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
            "contents": info_contents
        },
        # 操作按鈕
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#9C27B0",
                    "action": {
                        "type": "message",
                        "label": "查看所有筆記",
                        "text": "查看我的筆記"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "action": {
                        "type": "message", 
                        "label": "返回主選單",
                        "text": "主選單"
                    }
                }
            ],
            "margin": "xxl",
            "spacing": "sm"
        },
        {
            "type": "text",
            "text": f"筆記ID: #{note_id}",
            "color": "#999999",
            "size": "xs",
            "align": "center",
            "margin": "md"
        }
    ])
    
    # 添加樣式
    flex_message["styles"] = {
        "footer": {
            "separator": True
        }
    }
    
    try:
        line_bot_api.push_message(
            line_user_id,
            FlexSendMessage(alt_text="筆記創建成功", contents=flex_message)
        )
        return True
    except Exception as e:
        print(f"發送筆記創建消息失敗: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# 缺交學生通知功能
# ═══════════════════════════════════════════════════════════════

def notify_unsubmitted_students_from_cache(teacher_line_user_id: str, course_id: str, coursework_id: str):
    """
    從資料庫暫存讀取缺交學生資料並自動通知
    系統會自動判斷學生是否有LINE帳號，選擇合適的通知方式
    
    Args:
        teacher_line_user_id (str): 教師的LINE用戶ID
        course_id (str): Google Classroom課程ID
        coursework_id (str): Google Classroom作業ID
        
    Returns:
        dict: 通知結果統計
    """
    try:
        # 取得資料庫暫存的缺交學生資料
        from line_bot.models import HomeworkStatisticsCache
        from django.utils import timezone
        
        cached_data = HomeworkStatisticsCache.get_valid_cache(
            line_user_id=teacher_line_user_id,
            course_id=course_id,
            coursework_id=coursework_id
        )
        
        if not cached_data or not cached_data.is_valid():
            return {
                "error": "沒有找到有效的作業統計暫存資料",
                "message": "請先查詢作業狀態以取得最新資料"
            }
        
        unsubmitted_students = cached_data.unsubmitted_students
        homework_title = cached_data.homework_title
        
        # 取得教師資料和Google憑證
        from user.models import LineProfile
        from user.utils import get_valid_google_credentials
        
        teacher_profile = LineProfile.objects.get(line_user_id=teacher_line_user_id)
        creds = get_valid_google_credentials(teacher_profile)
        
        # 建立Google服務
        from googleapiclient.discovery import build
        service = build("classroom", "v1", credentials=creds, cache_discovery=False)
        
        # 統計結果
        results = {
            "total_students": len(unsubmitted_students),
            "line_notified": 0,
            "email_notified": 0,
            "failed": 0,
            "notification_details": []
        }
        
        for student in unsubmitted_students:
            student_email = student.get('emailAddress', '')
            student_name = student.get('name', '未知學生')
            student_id = student.get('userId', '')
            
            # 檢查學生是否有LINE帳號（透過email查詢）
            line_profile = LineProfile.objects.filter(email=student_email).first()
            
            notification_detail = {
                "student_name": student_name,
                "student_email": student_email,
                "method": "",
                "success": False,
                "error": ""
            }
            
            if line_profile and line_profile.line_user_id:
                # 學生有LINE帳號 - 發送LINE通知
                try:
                    send_homework_reminder_line(
                        line_profile.line_user_id,
                        homework_title,
                        course_id,
                        teacher_profile.name or "老師"
                    )
                    results["line_notified"] += 1
                    notification_detail["method"] = "LINE"
                    notification_detail["success"] = True
                    
                except Exception as e:
                    results["failed"] += 1
                    notification_detail["method"] = "LINE"
                    notification_detail["error"] = str(e)
                    print(f"LINE通知失敗 ({student_name}): {e}")
            else:
                # 學生沒有LINE帳號 - 發送email通知（透過Google Classroom）
                try:
                    send_homework_reminder_email(
                        service,
                        course_id,
                        coursework_id,
                        student_id,
                        homework_title,
                        teacher_profile.name or "老師"
                    )
                    results["email_notified"] += 1
                    notification_detail["method"] = "Email"
                    notification_detail["success"] = True
                    
                except Exception as e:
                    results["failed"] += 1
                    notification_detail["method"] = "Email"
                    notification_detail["error"] = str(e)
                    print(f"Email通知失敗 ({student_name}): {e}")
            
            results["notification_details"].append(notification_detail)
        
        # 發送通知結果給教師
        send_notification_result_to_teacher(teacher_line_user_id, homework_title, results)
        
        return results
        
    except Exception as e:
        print(f"從暫存通知缺交學生失敗: {e}")
        return {
            "error": "通知功能發生錯誤",
            "details": str(e)
        }

def notify_unsubmitted_students(teacher_line_user_id: str, course_id: str, homework_title: str, unsubmitted_students: list):
    """
    自動通知缺交學生（舊版本，保留向後兼容）
    系統會自動判斷學生是否有LINE帳號，選擇合適的通知方式
    
    Args:
        teacher_line_user_id (str): 教師的LINE用戶ID
        course_id (str): Google Classroom課程ID
        homework_title (str): 作業標題
        unsubmitted_students (list): 缺交學生列表，包含學生資料
        
    Returns:
        dict: 通知結果統計
    """
    try:
        # 取得教師資料和Google憑證
        from user.models import LineProfile
        from user.utils import get_valid_google_credentials
        
        teacher_profile = LineProfile.objects.get(line_user_id=teacher_line_user_id)
        creds = get_valid_google_credentials(teacher_profile)
        
        # 建立Google服務
        from googleapiclient.discovery import build
        service = build("classroom", "v1", credentials=creds, cache_discovery=False)
        
        # 統計結果
        results = {
            "total_students": len(unsubmitted_students),
            "line_notified": 0,
            "email_notified": 0,
            "failed": 0,
            "notification_details": []
        }
        
        for student in unsubmitted_students:
            student_email = student.get('emailAddress', '')
            student_name = student.get('name', {}).get('fullName', '未知學生')
            student_id = student.get('userId', '')
            
            # 檢查學生是否有LINE帳號（透過email查詢）
            line_profile = LineProfile.objects.filter(email=student_email).first()
            
            notification_detail = {
                "student_name": student_name,
                "student_email": student_email,
                "method": "",
                "success": False,
                "error": ""
            }
            
            if line_profile and line_profile.line_user_id:
                # 學生有LINE帳號 - 發送LINE通知
                try:
                    send_homework_reminder_line(
                        line_profile.line_user_id,
                        homework_title,
                        course_id,
                        teacher_profile.name or "老師"
                    )
                    results["line_notified"] += 1
                    notification_detail["method"] = "LINE"
                    notification_detail["success"] = True
                    
                except Exception as e:
                    results["failed"] += 1
                    notification_detail["method"] = "LINE"
                    notification_detail["error"] = str(e)
                    print(f"LINE通知失敗 ({student_name}): {e}")
            else:
                # 學生沒有LINE帳號 - 發送email通知（透過Google Classroom）
                try:
                    send_homework_reminder_email(
                        service,
                        course_id,
                        coursework_id,
                        student_id,
                        homework_title,
                        teacher_profile.name or "老師"
                    )
                    results["email_notified"] += 1
                    notification_detail["method"] = "Email"
                    notification_detail["success"] = True
                    
                except Exception as e:
                    results["failed"] += 1
                    notification_detail["method"] = "Email"
                    notification_detail["error"] = str(e)
                    print(f"Email通知失敗 ({student_name}): {e}")
            
            results["notification_details"].append(notification_detail)
        
        # 發送通知結果給教師
        send_notification_result_to_teacher(teacher_line_user_id, homework_title, results)
        
        return results
        
    except Exception as e:
        print(f"通知缺交學生失敗: {e}")
        return {
            "total_students": len(unsubmitted_students),
            "line_notified": 0,
            "email_notified": 0,
            "failed": len(unsubmitted_students),
            "error": str(e)
        }

def send_homework_reminder_line(student_line_user_id: str, homework_title: str, course_id: str, teacher_name: str, coursework_id: str = None):
    """
    發送作業提醒LINE訊息給學生
    
    Args:
        student_line_user_id (str): 學生的LINE用戶ID
        homework_title (str): 作業標題
        course_id (str): 課程ID
        teacher_name (str): 教師姓名
    """
    from .utils_encoding import create_google_classroom_assignment_url, create_google_classroom_course_url
    
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "⚠️ 作業提醒",
                    "weight": "bold",
                    "color": "#FF6B35",
                    "size": "lg"
                }
            ],
            "backgroundColor": "#FFF4E6"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"您還有作業尚未繳交：",
                    "size": "md",
                    "color": "#333333",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": homework_title,
                    "size": "lg",
                    "weight": "bold",
                    "color": "#FF6B35",
                    "wrap": True,
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"來自：{teacher_name}",
                            "size": "sm",
                            "color": "#666666"
                        },
                        {
                            "type": "text",
                            "text": "請盡快完成並繳交作業，避免影響成績。",
                            "size": "sm",
                            "color": "#666666",
                            "wrap": True,
                            "margin": "sm"
                        }
                    ],
                    "margin": "lg"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#FF6B35",
                    "action": {
                        "type": "uri",
                        "label": "前往Google Classroom",
                        "uri": create_google_classroom_assignment_url(course_id, coursework_id) if coursework_id else create_google_classroom_course_url(course_id)
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "action": {
                        "type": "message",
                        "label": "查看我的未交作業",
                        "text": "查看我的未交作業清單"
                    }
                }
            ],
            "spacing": "sm"
        }
    }
    
    try:
        line_bot_api.push_message(
            student_line_user_id,
            FlexSendMessage(alt_text=f"作業提醒 - {homework_title}", contents=flex_message)
        )
        return True
    except Exception as e:
        print(f"發送LINE作業提醒失敗: {e}")
        raise e

def send_homework_reminder_email(service, course_id: str, coursework_id: str, student_id: str, homework_title: str, teacher_name: str):
    """
    透過Gmail SMTP發送作業提醒email給學生
    
    Args:
        service: Google Classroom服務物件
        course_id (str): 課程ID
        coursework_id (str): 作業ID
        student_id (str): 學生的Google用戶ID
        homework_title (str): 作業標題
        teacher_name (str): 教師姓名
    """
    
    try:
        # 獲取學生的email地址
        student_profile = service.userProfiles().get(userId=student_id).execute()
        student_email = student_profile.get("emailAddress")
        student_name = student_profile.get("name", {}).get("fullName", "同學")
        
        if not student_email:
            raise Exception("無法獲取學生的email地址")
        
        # Gmail SMTP 設定
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv("GMAIL_USERNAME")  # 需要在.env中設定
        smtp_password = os.getenv("GMAIL_APP_PASSWORD")  # Gmail應用程式密碼
        
        if not smtp_username or not smtp_password:
            raise Exception("Gmail SMTP 設定不完整，請設定 GMAIL_USERNAME 和 GMAIL_APP_PASSWORD")
        
        # 建立email內容
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib
        from .utils_encoding import encode_course_id_for_google_classroom, create_google_classroom_course_url, create_google_classroom_assignment_url
        
        # 生成正確的 Google Classroom 連結
        classroom_link = create_google_classroom_assignment_url(course_id, coursework_id)
        
        # 建立郵件物件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📝 作業提醒：{homework_title}"
        msg['From'] = f"{teacher_name} <{smtp_username}>"
        msg['To'] = student_email
        
        # 純文字版本
        text_content = f"""親愛的{student_name}，

您好！這是來自 {teacher_name} 的作業提醒。

📚 課程作業通知
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 作業名稱：{homework_title}
⚠️  狀態：尚未繳交
🎯 請盡快完成並提交作業

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 溫馨提醒：
• 請登入 Google Classroom 查看詳細作業內容
• 如有任何問題，請透過 Classroom 與老師聯繫
• 請在截止日期前完成提交，避免影響成績

祝學習愉快！

{teacher_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
此為系統自動發送的提醒郵件，請勿直接回覆此郵件。
如需協助，請透過 Google Classroom 聯繫老師。
"""
        
        # HTML版本
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .homework-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .homework-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                .status-warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .tips {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                .btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 作業提醒通知</h1>
                    <p>來自 {teacher_name} 的訊息</p>
                </div>
                
                <div class="content">
                    <p>親愛的 <strong>{student_name}</strong>，您好！</p>
                    
                    <div class="homework-box">
                        <div class="homework-title">📚 {homework_title}</div>
                        <div class="status-warning">
                            <strong>⚠️ 提醒：</strong> 此作業尚未繳交，請盡快完成提交。
                        </div>
                    </div>
                    
                    <div class="tips">
                        <h4>💡 操作指引：</h4>
                        <ul>
                            <li>請登入 <strong>Google Classroom</strong> 查看詳細作業內容</li>
                            <li>確認作業要求和截止日期</li>
                            <li>完成作業後記得點擊「繳交」按鈕</li>
                            <li>如有疑問，可透過 Classroom 私訊功能聯繫老師</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{classroom_link}" class="btn">前往 Google Classroom</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>祝您學習愉快！<br><strong>{teacher_name}</strong></p>
                    <hr style="margin: 15px 0;">
                    <p>此為系統自動發送的提醒郵件，請勿直接回覆。<br>如需協助，請透過 Google Classroom 聯繫老師。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 加入純文字和HTML版本
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # 發送郵件
        try:
            # 建立SMTP連線
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # 啟用TLS加密
            server.login(smtp_username, smtp_password)
            
            # 發送郵件
            text = msg.as_string()
            server.sendmail(smtp_username, student_email, text)
            server.quit()
            
            print(f"✅ 已透過Gmail SMTP發送作業提醒給 {student_name} ({student_email})")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Gmail SMTP 認證失敗: {e}")
            print("請檢查 GMAIL_USERNAME 和 GMAIL_APP_PASSWORD 設定")
            raise e
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP 發送失敗: {e}")
            raise e
        
    except Exception as e:
        print(f"❌ 發送email作業提醒失敗: {e}")
        raise e

def send_notification_result_to_teacher(teacher_line_user_id: str, homework_title: str, results: dict):
    """
    發送通知結果給教師
    
    Args:
        teacher_line_user_id (str): 教師的LINE用戶ID
        homework_title (str): 作業標題
        results (dict): 通知結果統計
    """
    
    total = results.get('total_students', 0)
    line_notified = results.get('line_notified', 0)
    email_notified = results.get('email_notified', 0)
    failed = results.get('failed', 0)
    
    # 建立結果摘要
    success_rate = round(((line_notified + email_notified) / total * 100), 1) if total > 0 else 0
    
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📤 通知發送完成",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "lg"
                }
            ],
            "backgroundColor": "#F0F9F0"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": homework_title,
                    "size": "md",
                    "weight": "bold",
                    "wrap": True,
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "總計學生",
                                    "size": "sm",
                                    "color": "#666666"
                                },
                                {
                                    "type": "text",
                                    "text": f"{total} 人",
                                    "size": "sm",
                                    "color": "#333333",
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "LINE通知",
                                    "size": "sm",
                                    "color": "#666666"
                                },
                                {
                                    "type": "text",
                                    "text": f"{line_notified} 人",
                                    "size": "sm",
                                    "color": "#1DB446",
                                    "align": "end"
                                }
                            ],
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "Email通知",
                                    "size": "sm",
                                    "color": "#666666"
                                },
                                {
                                    "type": "text",
                                    "text": f"{email_notified} 人",
                                    "size": "sm",
                                    "color": "#2196F3",
                                    "align": "end"
                                }
                            ],
                            "margin": "sm"
                        }
                    ],
                    "margin": "lg"
                }
            ]
        }
    }
    
    # 如果有失敗的通知，添加失敗資訊
    if failed > 0:
        flex_message["body"]["contents"].append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "通知失敗",
                    "size": "sm",
                    "color": "#666666"
                },
                {
                    "type": "text",
                    "text": f"{failed} 人",
                    "size": "sm",
                    "color": "#FF4444",
                    "align": "end"
                }
            ],
            "margin": "sm"
        })
    
    # 添加成功率
    flex_message["body"]["contents"].extend([
        {
            "type": "separator",
            "margin": "lg"
        },
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "通知成功率",
                    "size": "md",
                    "weight": "bold",
                    "color": "#333333"
                },
                {
                    "type": "text",
                    "text": f"{success_rate}%",
                    "size": "md",
                    "weight": "bold",
                    "color": "#1DB446",
                    "align": "end"
                }
            ],
            "margin": "lg"
        }
    ])
    
    try:
        line_bot_api.push_message(
            teacher_line_user_id,
            FlexSendMessage(alt_text=f"通知發送完成 - {homework_title}", contents=flex_message)
        )
        return True
    except Exception as e:
        print(f"發送通知結果失敗: {e}")
        return False