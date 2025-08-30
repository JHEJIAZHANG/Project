# line_bot/flex_templates.py
"""
Flex Message 模板庫
提供各種功能選單的 Flex Message 模板

主要功能：
1. 基本功能選單（Bubble 類型）
2. 滾動式指南（Carousel 類型）
3. 註冊相關 Flex Message
4. 動態自定義 Carousel 生成
5. 模板管理和分類
"""

import os
import json
from .utils_encoding import encode_course_id_for_google_classroom, create_google_classroom_course_url, create_google_classroom_assignment_url

# ═══════════════════════════════════════════════════════════════
# 註冊相關 Flex Message 模板
# ═══════════════════════════════════════════════════════════════

def get_start_register_flex():
    """
    滾動式開始註冊指南 Flex Message
    3個步驟的 Carousel 設計，最後一步包含註冊按鈕
    """
    return {
        "type": "flex",
        "altText": "開始註冊",
        "contents": {
            "type": "carousel",
            "contents": [
                # Step 1 - 歡迎
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 1",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#4CAF50",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "歡迎使用智能課程管理系統！",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#333333",
                                "margin": "md",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "這是一個專為教師和學生設計的智能課程管理系統，讓您輕鬆管理課程、作業和行事曆。",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                # Step 2 - 功能介紹
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 2",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "豐富功能等您探索",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#333333",
                                "margin": "md",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "📚 課程管理：建立和管理您的課程\n📝 作業系統：輕鬆發布和收取作業\n📅 行事曆：重要事件提醒\n📓 筆記功能：記錄學習重點",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                # Step 3 - 開始使用
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 3",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#4CAF50",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "立即開始使用",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#333333",
                                "margin": "md",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "點擊下方按鈕完成註冊，開始您的智能教學之旅！註冊後即可使用所有功能。",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "開始註冊",
                                    "uri": f"https://liff.line.me/{os.getenv('VITE_LIFF_ID')}"
                                },
                                "style": "primary",
                                "color": "#4CAF50",
                                "height": "sm",
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "spacing": "sm"
                    }
                }
            ]
        }
    }

def get_register_done_flex(name: str, role: str):
    """
    註冊成功 Flex Message 
    顯示成功訊息和用戶資訊
    """
    return {
        "type": "flex",
        "altText": "註冊成功",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "24px",
                "spacing": "lg",
                "contents": [
                    # 成功標題
                    {
                        "type": "text",
                        "text": "🎉 註冊成功",
                        "size": "xxl",
                        "weight": "bold",
                        "color": "#4CAF50",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"歡迎 {name} 加入我們！",
                        "size": "lg",
                        "color": "#1C1C1E",
                        "align": "center",
                        "wrap": True,
                        "margin": "sm"
                    },
                    # 分隔線
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7"
                    },
                    # 用戶資訊
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "paddingAll": "16px",
                        "backgroundColor": "#F2F2F7",
                        "cornerRadius": "12px",
                        "margin": "xl",
                        "contents": [
                            {
                                "type": "text",
                                "text": "👤" if role != 'teacher' else "👨‍🏫",
                                "size": "xl",
                                "flex": 0
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "身份類型",
                                        "size": "sm",
                                        "color": "#8E8E93"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{'🎓 教師' if role == 'teacher' else '📚 學生'}",
                                        "size": "md",
                                        "weight": "bold",
                                        "color": "#4CAF50",
                                        "margin": "xs"
                                    }
                                ]
                            }
                        ]
                    },
                    # 成功狀態
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "paddingAll": "12px",
                        "backgroundColor": "#E8F5E8",
                        "cornerRadius": "8px",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "✅",
                                "flex": 0,
                                "size": "sm"
                            },
                            {
                                "type": "text",
                                "text": "帳號綁定完成，所有功能已啟用",
                                "flex": 1,
                                "size": "sm",
                                "color": "#2E7D32",
                                "weight": "bold",
                                "wrap": True
                            }
                        ]
                    },
                    # 下一步提示
                    {
                        "type": "text",
                        "text": "📱 現在您可以開始使用所有功能了！\n功能選單即將為您開啟...",
                        "size": "sm",
                        "color": "#8E8E93",
                        "align": "center",
                        "wrap": True,
                        "margin": "xl"
                    }
                ]
            }
        }
    }

# ═══════════════════════════════════════════════════════════════
# 基本功能選單模板（Bubble 類型）
# ═══════════════════════════════════════════════════════════════

def get_main_menu_flex():
    """
    主功能選單 Flex Message 
    """
    return {
        "type": "flex",
        "altText": "功能選單",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",  # 整個泡泡的圓角
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "none",
                "paddingAll": "20px",
                "backgroundColor": "#F8F9FA",
                "cornerRadius": "20px",  # 內容區域的圓角
                "contents": [
                    # 標題區域
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "none",
                        "paddingBottom": "24px",
                        "contents": [
                            {
                                "type": "text",
                                "text": "功能選單",
                                "weight": "bold",
                                "size": "28px",
                                "color": "#1D1D1F",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "選擇您需要的功能",
                                "size": "15px",
                                "color": "#86868B",
                                "align": "center",
                                "margin": "sm"
                            }
                        ]
                    },
                    
                    # 功能按鈕區域
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "12px",
                        "contents": [
                            # 第一排按鈕
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "12px",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "spacing": "none",
                                        "backgroundColor": "#FFFFFF",
                                        "cornerRadius": "18px",  # 按鈕圓角
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        # 添加邊框效果
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "課程管理"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "📚",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "課程",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical", 
                                        "spacing": "none",
                                        "backgroundColor": "#FFFFFF",
                                        "cornerRadius": "18px",
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "作業管理"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "📝",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "作業",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    }
                                ]
                            },
                            
                            # 第二排按鈕
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "12px",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "spacing": "none",
                                        "backgroundColor": "#FFFFFF",
                                        "cornerRadius": "18px",
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "行事曆管理"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "📅",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "行事曆",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "spacing": "none", 
                                        "backgroundColor": "#FFFFFF",
                                        "cornerRadius": "18px",
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "筆記管理"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "📓",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "筆記",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    }
                                ]
                            },
                            
                            # 第三排按鈕
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "12px",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "spacing": "none",
                                        "backgroundColor": "#FFFFFF", 
                                        "cornerRadius": "18px",
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "帳戶設定"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "⚙️",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "設定",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "spacing": "none",
                                        "backgroundColor": "#FFFFFF",
                                        "cornerRadius": "18px", 
                                        "paddingAll": "20px",
                                        "flex": 1,
                                        "borderWidth": "1px",
                                        "borderColor": "#E8E8ED",
                                        "action": {
                                            "type": "message",
                                            "text": "使用說明"
                                        },
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "❓",
                                                "size": "32px",
                                                "align": "center",
                                                "margin": "none"
                                            },
                                            {
                                                "type": "text",
                                                "text": "說明",
                                                "size": "16px",
                                                "weight": "bold",
                                                "color": "#1D1D1F",
                                                "align": "center",
                                                "margin": "sm"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }


def get_course_menu_flex():
    """
    課程管理功能選單 
    提供課程的 CRUD 操作選項
    """
    return {
        "type": "flex",
        "altText": "課程管理",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "lg",
                "paddingAll": "24px",
                "cornerRadius": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "📚 課程管理",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "margin": "xl",
                        "cornerRadius": "18px",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "➕ 建立新課程",
                                    "text": "我要建立新課程"
                                },
                                                        "style": "primary",
                        "color": "#007AFF",
                        "height": "md",
                        "cornerRadius": "18px"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "📋 我的課程",
                                    "text": "查看我的所有課程"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "刪除課程",
                                    "text": "刪除課程"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "❓ 建立指南",
                                    "text": "課程建立指南"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "← 返回主選單",
                            "text": "功能選單"
                        },
                        "style": "link",
                        "color": "#8E8E93",
                        "cornerRadius": "14px"
                    }
                ]
            }
        }
    }

def get_homework_menu_flex():
    """
    作業管理功能選單 
    提供作業的管理和查看功能
    """
    return {
        "type": "flex",
        "altText": "作業管理",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "lg",
                "paddingAll": "24px",
                "cornerRadius": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "📝 作業管理",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "margin": "xl",
                        "cornerRadius": "18px",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "➕ 新增作業",
                                    "text": "我要新增作業"
                                },
                                                        "style": "primary",
                        "color": "#007AFF",
                        "height": "md",
                        "cornerRadius": "18px"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "📋 我的作業",
                                    "text": "查看我的所有作業"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "📊 提交狀況",
                                    "text": "查看作業提交狀況"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "❓ 建立指南",
                                    "text": "作業建立指南"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "← 返回主選單",
                            "text": "功能選單"
                        },
                        "style": "link",
                        "color": "#8E8E93",
                        "cornerRadius": "14px"
                    }
                ]
            }
        }
    }

def get_calendar_menu_flex():
    """
    行事曆管理功能選單 
    提供事件的新增、查看和管理功能
    """
    return {
        "type": "flex",
        "altText": "行事曆管理",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "lg",
                "paddingAll": "24px",
                "cornerRadius": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "📅 行事曆管理",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "margin": "xl",
                        "cornerRadius": "18px",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "➕ 新增事件",
                                    "text": "我要新增行事曆事件"
                                },
                                                        "style": "primary",
                        "color": "#007AFF",
                        "height": "md",
                        "cornerRadius": "18px"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "📅 查看行事曆",
                                    "text": "查看我的行事曆"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "👥 管理參與者",
                                    "text": "管理事件參與者"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "⚙️ 修改事件",
                                    "text": "修改行事曆事件"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "← 返回主選單",
                            "text": "功能選單"
                        },
                        "style": "link",
                        "color": "#8E8E93",
                        "cornerRadius": "14px"
                    }
                ]
            }
        }
    }

def get_notes_menu_flex():
    """
    筆記管理功能選單 
    提供筆記的建立、編輯和搜尋功能
    """
    return {
        "type": "flex",
        "altText": "筆記管理",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "lg",
                "paddingAll": "24px",
                "cornerRadius": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "📓 筆記管理",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "margin": "xl",
                        "cornerRadius": "18px",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "➕ 建立筆記",
                                    "text": "我要建立新筆記"
                                },
                                                        "style": "primary",
                        "color": "#007AFF",
                        "height": "md",
                        "cornerRadius": "18px"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "📄 我的筆記",
                                    "text": "查看我的所有筆記"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "🔍 搜尋筆記",
                                    "text": "搜尋我的筆記"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "✏️ 編輯筆記",
                                    "text": "編輯已存在的筆記"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "← 返回主選單",
                            "text": "功能選單"
                        },
                        "style": "link",
                        "color": "#8E8E93",
                        "cornerRadius": "14px"
                    }
                ]
            }
        }
    }

def get_account_menu_flex():
    """
    帳戶設定功能選單 
    提供個人資料和隱私設定功能
    """
    return {
        "type": "flex",
        "altText": "帳戶設定",
        "contents": {
            "type": "bubble",
            "size": "giga",
            "cornerRadius": "24px",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "lg",
                "paddingAll": "24px",
                "cornerRadius": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "⚙️ 帳戶設定",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "margin": "xl",
                        "cornerRadius": "18px",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "👤 個人資料",
                                    "text": "查看我的個人資料"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "🔗 Google 綁定",
                                    "text": "管理 Google 帳號綁定"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "🔔 通知設定",
                                    "text": "管理通知設定"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "🔒 隱私設定",
                                    "text": "管理隱私設定"
                                },
                                "style": "secondary",
                                "color": "#F2F2F7",
                                "height": "md"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#F2F2F7",
                        "cornerRadius": "4px"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "← 返回主選單",
                            "text": "功能選單"
                        },
                        "style": "link",
                        "color": "#8E8E93",
                        "cornerRadius": "14px"
                    }
                ]
            }
        }
    }



# ═══════════════════════════════════════════════════════════════
# Carousel 滾動式指南模板
# ═══════════════════════════════════════════════════════════════

def get_course_creation_guide_carousel():
    """
    課程建立步驟指南 - 滾動式展示
    5個步驟的課程建立完整流程
    """
    return {
        "type": "flex",
        "altText": "課程建立步驟指南",
        "contents": {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 1",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "1. 點選【新增課程】",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "首先需要綁定你的 Google 帳號以存取 Classroom",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 2",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "點選【管理帳號】進行設定",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "在管理帳號頁面中，完成 Google 帳號的授權流程",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 3",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "點擊下方【新增】後進入編輯頁面",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "可以選擇【學科/部門/狀態】三種類型預設",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 4",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "輸入『功能選單』快速查看可用操作",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "快速進入課程、作業、行事曆等功能",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 5",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "明細中也可以直接登記預算",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "例如：刪除 作業 國文作業一",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                }
            ]
        }
    }

def get_homework_creation_guide_carousel():
    """
    作業建立步驟指南 - 滾動式展示
    6個步驟的作業建立完整流程
    """
    return {
        "type": "flex",
        "altText": "作業建立步驟指南",
        "contents": {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 1",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "用自然語言新增作業",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "新增作業 國文作業一",
                                        "size": "xs",
                                        "color": "#4CAF50",
                                        "backgroundColor": "#E8F5E8",
                                        "paddingAll": "4px"
                                    },
                                    {
                                        "type": "text",
                                        "text": "截止 10/15",
                                        "size": "xs",
                                        "color": "#FF6B35",
                                        "weight": "bold"
                                    }
                                ],
                                "margin": "md",
                                "spacing": "sm"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "也可指定課程、截止日期、說明等細節",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 2",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "系統會回覆建立作業確認",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "新增作業 國文作業一",
                                "size": "lg",
                                "color": "#4CAF50",
                                "weight": "bold",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "可補充/修改作業標題或說明",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 3",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "查看指定作業提交狀況",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                                                         {
                                 "type": "button",
                                 "action": {
                                     "type": "uri",
                                     "label": "前往頁面",
                                     "uri": "https://example.com"
                                 },
                                 "style": "primary",
                                 "color": "#FF5722",
                                 "height": "sm",
                                 "margin": "md"
                             },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "例如：查看 作業 國文作業一 提交狀況",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 4",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "查看我的所有作業",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "例如：查看 我的作業",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 5",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "常用操作",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• 新增作業\n• 查看提交狀況\n• 查看我的作業\n• 刪除作業",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "Tips",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#4CAF50",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "小技巧",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "可直接用自然語言操作所有作業功能",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#E8F5E8"
                    }
                }
            ]
        }
    }

def get_system_usage_guide_carousel():
    """
    系統使用指南 - 滾動式展示
    5個步驟的系統使用完整教學
    """
    return {
        "type": "flex",
        "altText": "系統使用指南",
        "contents": {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 1",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "首次使用請先註冊帳號",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "點擊下方註冊按鈕開始使用",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            },
                                                         {
                                 "type": "button",
                                 "action": {
                                     "type": "message",
                                     "label": "開始註冊",
                                     "text": "開始註冊"
                                 },
                                 "style": "primary",
                                 "color": "#4CAF50",
                                 "height": "sm",
                                 "margin": "md"
                             }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 2",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "綁定 Google 帳號",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "連接你的 Google Classroom 帳號以同步課程資料",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            },
                                                         {
                                 "type": "button",
                                 "action": {
                                     "type": "message",
                                     "label": "綁定 Google 帳號",
                                     "text": "綁定 Google 帳號"
                                 },
                                 "style": "secondary",
                                 "height": "sm",
                                 "margin": "md"
                             }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 3",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "建立你的第一個課程",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "透過課程管理功能建立課程並邀請學生",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            },
                                                         {
                                 "type": "button",
                                 "action": {
                                     "type": "message",
                                     "label": "建立課程",
                                     "text": "建立課程"
                                 },
                                 "style": "primary",
                                 "color": "#2196F3",
                                 "height": "sm",
                                 "margin": "md"
                             }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "STEP 4",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#FF6B35",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "開始使用各項功能",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• 建立作業\n• 管理行事曆\n• 記錄筆記\n• 追蹤進度",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#FFF4E6"
                    }
                },
                {
                    "type": "bubble",
                    "size": "kilo",
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
                                        "text": "完成！",
                                        "color": "#FFFFFF",
                                        "size": "xs",
                                        "weight": "bold"
                                    }
                                ],
                                "backgroundColor": "#4CAF50",
                                "paddingAll": "8px",
                                "cornerRadius": "6px",
                                "margin": "none"
                            },
                            {
                                "type": "text",
                                "text": "🎉 開始享受智能教學管理！",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md",
                                "weight": "bold"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "如有問題，隨時輸入「功能選單」查看更多選項",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "md"
                            },
                                                         {
                                 "type": "button",
                                 "action": {
                                     "type": "message",
                                     "label": "功能選單",
                                     "text": "功能選單"
                                 },
                                 "style": "link",
                                 "height": "sm",
                                 "margin": "md"
                             }
                        ],
                        "paddingAll": "16px",
                        "backgroundColor": "#E8F5E8"
                    }
                }
            ]
        }
    }

# ═══════════════════════════════════════════════════════════════
# 課程查看模板
# ═══════════════════════════════════════════════════════════════

def get_course_view_flex(courses: list):
    """
    課程查看 Flex Message - 動態課程列表
    適用於查看所有課程及作業狀況
    
    Args:
        courses (list): 課程列表，每個課程應包含 name 和 id 欄位
    """
    # 建立課程項目
    course_items = []
    colors = ["#FF6B35", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", 
              "#2196F3", "#00BCD4", "#009688", "#4CAF50", "#8BC34A"]
    
    for i, course in enumerate(courses):
        color = colors[i % len(colors)]  # 循環使用顏色
        
        course_item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(i + 1),
                            "size": "sm",
                            "color": "#ffffff",
                            "weight": "bold",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": color,
                    "cornerRadius": "50px",
                    "width": "32px",
                    "height": "32px",
                    "justifyContent": "center",
                    "flex": 0
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": course["name"],
                            "weight": "bold",
                            "size": "md",
                            "color": "#2C3E50"
                        },
                        {
                            "type": "text",
                            "text": "點擊進入課堂",
                            "size": "xs",
                            "color": "#6C757D",
                            "margin": "xs"
                        }
                    ],
                    "flex": 1,
                    "margin": "md",
                    "action": {
                        "type": "uri", 
                        "uri": create_google_classroom_course_url(course['id'])
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "▶",
                            "size": "lg",
                            "color": "#007bff",
                            "align": "center",
                            "gravity": "center"
                        }
                    ],
                    "flex": 0,
                    "width": "40px",
                    "height": "40px",
                    "backgroundColor": "#E3F2FD",
                    "cornerRadius": "20px",
                    "justifyContent": "center",
                    "action": {
                        "type": "message",
                        "text": f"查看{course['name']}作業提交狀況"
                    }
                }
            ],
            "paddingAll": "12px",
            "backgroundColor": "#f8f9fa",
            "cornerRadius": "8px",
            "margin": "md" if i == 0 else "sm",
            "spacing": "md"
        }
        course_items.append(course_item)
    
    # 建立完整的 Flex Message
    return {
        "type": "flex",
        "altText": f"查看 {len(courses)} 個課程",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🐦",
                                "size": "xl",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": "您好！歡迎回來",
                                "weight": "bold",
                                "size": "xl",
                                "color": "#ffffff",
                                "flex": 1,
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "點擊課程名稱進入課堂，點擊箭頭查看作業狀況",
                        "size": "sm",
                        "color": "#ffffff",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#007bff",
                "paddingAll": "20px"
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
                                "text": "📚",
                                "size": "md",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": "您的課程列表",
                                "weight": "bold",
                                "size": "md",
                                "color": "#2C3E50",
                                "flex": 1,
                                "margin": "sm"
                            }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#E9ECEF"
                    }
                ] + course_items,
                "paddingAll": "16px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "💡",
                                "size": "sm",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": "點擊課程名稱進入 Google Classroom，點擊藍色箭頭查看作業狀況",
                                "size": "xs",
                                "color": "#6C757D",
                                "flex": 1,
                                "margin": "xs",
                                "wrap": True
                            }
                        ],
                        "backgroundColor": "#F0F8FF",
                        "paddingAll": "12px",
                        "cornerRadius": "6px"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "message",
                            "label": "🏠 返回主選單",
                            "text": "主選單"
                        },
                        "margin": "md",
                        "height": "sm"
                    }
                ],
                "paddingAll": "16px"
            }
        }
    }

# ═══════════════════════════════════════════════════════════════
# 作業提交統計模板（動態）
# ═══════════════════════════════════════════════════════════════

def get_homework_submission_stats_flex(course_name: str, homework_title: str, total: int, submitted: int, unsubmitted: int, course_id: str, homework_id: str):
    """
    作業提交統計 Flex Message（單一 bubble）
    參數化：課程名稱、作業標題、總人數、已繳交、未繳交，以及對應的課程/作業 ID。
    互動使用 Postback，避免將學生個資傳到 n8n。
    """
    return {
        "type": "flex",
        "altText": f"{course_name} - {homework_title} 提交統計",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 作業提交統計",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    },
                    {
                        "type": "text",
                        "text": f"{course_name} - {homework_title}",
                        "size": "sm",
                        "color": "#ffffff",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#007bff",
                "paddingAll": "20px"
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
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "📝", "size": "xl", "align": "center"},
                                    {"type": "text", "text": "總人數", "size": "xs", "color": "#666666", "align": "center"},
                                    {"type": "text", "text": str(total), "size": "xxl", "weight": "bold", "color": "#2C3E50", "align": "center"}
                                ],
                                "backgroundColor": "#f8f9fa",
                                "paddingAll": "12px",
                                "cornerRadius": "8px",
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "✅", "size": "xl", "align": "center"},
                                    {"type": "text", "text": "已繳交", "size": "xs", "color": "#666666", "align": "center"},
                                    {"type": "text", "text": str(submitted), "size": "xxl", "weight": "bold", "color": "#28a745", "align": "center"}
                                ],
                                "backgroundColor": "#d4edda",
                                "paddingAll": "12px",
                                "cornerRadius": "8px",
                                "flex": 1,
                                "margin": "sm"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "❌", "size": "xl", "align": "center"},
                                    {"type": "text", "text": "未繳交", "size": "xs", "color": "#666666", "align": "center"},
                                    {"type": "text", "text": str(unsubmitted), "size": "xxl", "weight": "bold", "color": "#dc3545", "align": "center"}
                                ],
                                "backgroundColor": "#f8d7da",
                                "paddingAll": "12px",
                                "cornerRadius": "8px",
                                "flex": 1,
                                "margin": "sm"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "📈 完成率", "size": "md", "weight": "bold", "flex": 0},
                            {"type": "text", "text": f"{round((submitted/total)*100, 1) if total else 0}% ({submitted}/{total})", "size": "md", "weight": "bold", "color": "#28a745", "align": "end", "flex": 1}
                        ],
                        "backgroundColor": "#e8f5e9",
                        "paddingAll": "12px",
                        "cornerRadius": "6px",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "📋 查看未繳交名單",
                            "data": f"submission:pending:{course_id}:{homework_id}"
                        },
                        "style": "primary",
                        "color": "#dc3545"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "📊 詳細統計",
                            "data": f"submission:stats:{course_id}:{homework_id}"
                        },
                        "style": "secondary",
                        "margin": "sm"
                    }
                ],
                "paddingAll": "16px"
            }
        }
    }

# ═══════════════════════════════════════════════════════════════
# 課程刪除確認模板
# ═══════════════════════════════════════════════════════════════

def get_course_deletion_confirmation_flex(courses: list):
    """
    課程刪除確認 Flex Message - 單一 Bubble 版本
    適用於課程數量 ≤ 10 的情況
    
    Args:
        courses (list): 課程列表，每個課程應包含 name 和 id 欄位
    """
    # 建立課程項目
    course_items = []
    colors = ["#FF5722", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", 
              "#2196F3", "#00BCD4", "#009688", "#4CAF50", "#8BC34A"]
    
    for i, course in enumerate(courses):
        color = colors[i % len(colors)]  # 循環使用顏色
        
        course_item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(i + 1),
                            "size": "sm",
                            "color": "#ffffff",
                            "weight": "bold",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": color,
                    "cornerRadius": "50px",
                    "width": "28px",
                    "height": "28px",
                    "justifyContent": "center",
                    "flex": 0
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": course["name"],
                            "size": "md",
                            "weight": "bold",
                            "color": "#2C3E50",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": f"ID: {course['id']}",
                            "size": "xs",
                            "color": "#7F8C8D",
                            "margin": "xs"
                        }
                    ],
                    "flex": 1,
                    "margin": "md"
                }
            ],
            "margin": "md",
            "paddingAll": "8px",
            "backgroundColor": "#F8F9FA",
            "cornerRadius": "8px"
        }
        course_items.append(course_item)
    
    # 建立完整的 Flex Message
    return {
        "type": "flex",
        "altText": f"刪除 {len(courses)} 個課程確認",
        "contents": {
            "type": "bubble",
            "size": "mega",  # 使用 mega 尺寸以容納更多內容
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⚠️",
                                "size": "xl",
                                "flex": 0
                            },
                            {
                                "type": "text",
                                "text": "刪除課程確認",
                                "weight": "bold",
                                "color": "#ffffff",
                                "size": "lg",
                                "flex": 1,
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": f"即將刪除 {len(courses)} 個課程",
                        "color": "#ffffff",
                        "size": "sm",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#E74C3C",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📚 課程列表",
                        "weight": "bold",
                        "size": "md",
                        "color": "#2C3E50"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    }
                ] + course_items + [
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
                                "text": "⚠️ 重要提醒",
                                "weight": "bold",
                                "color": "#E74C3C",
                                "size": "sm"
                            },
                            {
                                "type": "text",
                                "text": "• 此操作無法復原\n• 課程內所有作業和資料將被刪除\n• 學生將無法再訪問課程",
                                "color": "#7F8C8D",
                                "size": "xs",
                                "wrap": True,
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": "#FFF5F5",
                        "paddingAll": "12px",
                        "cornerRadius": "8px",
                        "margin": "md"
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
                        "color": "#E74C3C",
                        "action": {
                            "type": "message",
                            "label": "🗑️ 確認刪除全部課程",
                            "text": "確認刪除全部課程"
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "message",
                            "label": "❌ 取消操作",
                            "text": "取消刪除課程"
                        },
                        "margin": "sm"
                    }
                ]
            }
        }
    }

def get_course_deletion_confirmation_paginated_flex(courses: list, page_size: int = 8):
    """
    分頁顯示課程刪除確認 - Carousel 版本
    適用於課程數量 > 10 的情況
    
    Args:
        courses (list): 課程列表，每個課程應包含 name 和 id 欄位
        page_size (int): 每頁顯示的課程數量，預設為 8
    """
    total_pages = (len(courses) + page_size - 1) // page_size
    carousel_contents = []
    
    for page in range(total_pages):
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(courses))
        page_courses = courses[start_idx:end_idx]
        
        # 建立該頁的課程項目
        course_items = []
        colors = ["#FF5722", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", 
                  "#2196F3", "#00BCD4", "#009688"]
        
        for i, course in enumerate(page_courses):
            global_index = start_idx + i + 1
            color = colors[i % len(colors)]
            
            course_item = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": str(global_index),
                                "size": "xs",
                                "color": "#ffffff",
                                "weight": "bold",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": color,
                        "cornerRadius": "50px",
                        "width": "24px",
                        "height": "24px",
                        "justifyContent": "center",
                        "flex": 0
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": course["name"][:15] + ("..." if len(course["name"]) > 15 else ""),
                                "size": "sm",
                                "weight": "bold",
                                "color": "#2C3E50",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": f"ID: {course['id'][:12]}...",
                                "size": "xs",
                                "color": "#7F8C8D",
                                "margin": "xs"
                            }
                        ],
                        "flex": 1,
                        "margin": "sm"
                    }
                ],
                "margin": "sm",
                "paddingAll": "6px",
                "backgroundColor": "#F8F9FA",
                "cornerRadius": "6px"
            }
            course_items.append(course_item)
        
        # 建立該頁的 bubble
        page_bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"⚠️ 刪除確認 ({page + 1}/{total_pages})",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": f"第 {start_idx + 1}-{end_idx} 個課程",
                        "color": "#ffffff",
                        "size": "sm",
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#E74C3C",
                "paddingAll": "16px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": course_items
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": []
            }
        }
        
        # 只在最後一頁加確認按鈕
        if page == total_pages - 1:
            page_bubble["footer"]["contents"] = [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#E74C3C",
                    "action": {
                        "type": "message",
                        "label": f"🗑️ 確認刪除全部 {len(courses)} 個課程",
                        "text": "確認刪除全部課程"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "❌ 取消",
                        "text": "取消刪除課程"
                    },
                    "margin": "sm"
                }
            ]
        else:
            page_bubble["footer"]["contents"] = [
                {
                    "type": "text",
                    "text": "👉 請滑動查看更多課程",
                    "size": "xs",
                    "color": "#7F8C8D",
                    "align": "center"
                }
            ]
        
        carousel_contents.append(page_bubble)
    
    return {
        "type": "flex",
        "altText": f"刪除 {len(courses)} 個課程確認",
        "contents": {
            "type": "carousel",
            "contents": carousel_contents
        }
    }

# ═══════════════════════════════════════════════════════════════
# 模板管理和工具函數
# ═══════════════════════════════════════════════════════════════

def get_flex_template(template_name, **kwargs):
    """
    根據模板名稱獲取對應的 Flex Message
    
    Args:
        template_name (str): 模板名稱
        **kwargs: 模板所需的參數
        
    Returns:
        dict: Flex Message 模板，如果不存在則返回 None
    """
    # 動態調用模板函數，傳遞參數
    if template_name == "course_view" or template_name == "get_course_view":
        return get_course_view_flex(kwargs.get('courses', []))
    elif template_name == "course_deletion_confirmation":
        return get_course_deletion_confirmation_flex(kwargs.get('courses', []))
    elif template_name == "course_deletion_confirmation_paginated":
        return get_course_deletion_confirmation_paginated_flex(
            kwargs.get('courses', []), 
            kwargs.get('page_size', 8)
        )
    elif template_name == "teacher_homework_statistics":
        return get_teacher_homework_statistics_flex(
            kwargs.get('course_name', ''),
            kwargs.get('homework_title', ''),
            kwargs.get('statistics', {}),
            kwargs.get('unsubmitted_students', None)
        )
    elif template_name == "student_homework_status":
        # 處理 payload 參數（可能是字串或物件）
        payload_data = kwargs.get('payload', {})
        
        # 如果 payload_data 是字串，嘗試解析為 JSON
        if isinstance(payload_data, str):
            try:
                payload_data = json.loads(payload_data)
            except json.JSONDecodeError:
                payload_data = {}
        
        # 從 payload 或 kwargs 中獲取 homeworks
        homeworks = payload_data.get('homeworks', kwargs.get('homeworks', []))
        
        # 如果沒有 homeworks，返回錯誤提示
        if not homeworks:
            return {
                "type": "flex",
                "altText": "參數錯誤",
                "contents": {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "❌ 參數錯誤",
                                "weight": "bold",
                                "color": "#FF4444"
                            },
                            {
                                "type": "text",
                                "text": "缺少作業列表資料",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True
                            }
                        ]
                    }
                }
            }
        
        return get_student_homework_status_flex(homeworks)
    
    # 靜態模板（不需要參數）
    templates = {
        # 註冊相關模板
        "start_register": get_start_register_flex(),
        
        # 基本功能選單
        "main_menu": get_main_menu_flex(),
        "course_menu": get_course_menu_flex(),
        "homework_menu": get_homework_menu_flex(),
        "calendar_menu": get_calendar_menu_flex(),
        "notes_menu": get_notes_menu_flex(),
        "account_menu": get_account_menu_flex(),
        
        # Carousel 滾動式指南
        "course_creation_guide": get_course_creation_guide_carousel(),
        "homework_creation_guide": get_homework_creation_guide_carousel(),
        "system_usage_guide": get_system_usage_guide_carousel(),
    }
    
    return templates.get(template_name)

def get_available_templates():
    """
    獲取所有可用的模板名稱
    
    Returns:
        list: 模板名稱列表
    """
    return [
        # 註冊相關模板
        "start_register",
        
        # 基本功能選單
        "main_menu",
        "course_menu", 
        "homework_menu",
        "calendar_menu",
        "notes_menu",
        "account_menu",
        
        # Carousel 滾動式指南
        "course_creation_guide",
        "homework_creation_guide", 
        "system_usage_guide",
        
        # 課程管理模板
        "course_view",
        "get_course_view",  # 兼容性別名
        "course_deletion_confirmation",
        "course_deletion_confirmation_paginated",
        
        # 作業統計模板
        "teacher_homework_statistics",
        "student_homework_status",
    ]

def get_template_categories():
    """
    獲取模板分類資訊
    
    Returns:
        dict: 分類資訊
    """
    return {
        "功能選單": [
            "main_menu",
            "course_menu", 
            "homework_menu",
            "calendar_menu",
            "notes_menu",
            "account_menu"
        ],
        "使用指南": [
            "course_creation_guide",
            "homework_creation_guide",
            "system_usage_guide"
        ],
        "課程管理": [
            "course_view",
            "get_course_view",  # 兼容性別名
            "course_deletion_confirmation",
            "course_deletion_confirmation_paginated"
        ],
        "作業統計": [
            "teacher_homework_statistics",
            "student_homework_status"
        ]
    }

def create_custom_carousel(steps_data, title="操作步驟", alt_text="步驟指南"):
    """
    動態創建自定義的 Carousel 模板
    
    Args:
        steps_data (list): 步驟資料列表
        title (str): 標題
        alt_text (str): alt text
        
    Returns:
        dict: Flex Message Carousel 模板
    """
    carousel_contents = []
    
    for i, step in enumerate(steps_data, 1):
        step_type = step.get('type', 'STEP')
        step_title = step.get('title', f'{step_type} {i}')
        content = step.get('content', '')
        description = step.get('description', '')
        button_text = step.get('button_text', '')
        button_action = step.get('button_action', 'message')
        button_data = step.get('button_data', '')
        bg_color = step.get('bg_color', '#FFF4E6')
        badge_color = step.get('badge_color', '#FF6B35')
        
        bubble_content = {
            "type": "bubble",
            "size": "kilo",
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
                                "text": step_title,
                                "color": "#FFFFFF",
                                "size": "xs",
                                "weight": "bold"
                            }
                        ],
                        "backgroundColor": badge_color,
                        "paddingAll": "8px",
                        "cornerRadius": "6px",
                        "margin": "none"
                    },
                    {
                        "type": "text",
                        "text": content,
                        "size": "sm",
                        "color": "#333333",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "paddingAll": "16px",
                "backgroundColor": bg_color
            }
        }
        
        # 添加描述
        if description:
            bubble_content["body"]["contents"].insert(-1, {
                "type": "separator",
                "margin": "md"
            })
            bubble_content["body"]["contents"].insert(-1, {
                "type": "text",
                "text": description,
                "size": "xs",
                "color": "#666666",
                "wrap": True,
                "margin": "md"
            })
        
        # 添加按鈕
        if button_text and button_data:
             bubble_content["body"]["contents"].append({
                 "type": "button",
                 "action": {
                     "type": button_action,
                     "label": button_text,
                     "text" if button_action == "message" else "uri": button_data
                 },
                 "style": "primary" if step_type == "STEP" else "secondary",
                 "height": "sm",
                 "margin": "md"
             })
        
        carousel_contents.append(bubble_content)
    
    return {
        "type": "flex",
        "altText": alt_text,
        "contents": {
            "type": "carousel",
            "contents": carousel_contents
        }
    }

# ═══════════════════════════════════════════════════════════════
# 作業統計 Flex Message 模板
# ═══════════════════════════════════════════════════════════════

def get_teacher_homework_statistics_flex(course_name, homework_title, statistics, unsubmitted_students=None, course_id=None, coursework_id=None):
    """
    教師作業統計 Flex Message
    包含統計圖表、缺交學生名單、通知按鈕
    
    Args:
        course_name (str): 課程名稱
        homework_title (str): 作業標題
        statistics (dict): 統計數據
        unsubmitted_students (list): 缺交學生列表 (可選)
        course_id (str): Google Classroom 課程 ID (可選)
        coursework_id (str): Google Classroom 作業 ID (可選)
    """
    total_students = statistics.get('total_students', 0)
    submitted = statistics.get('submitted', 0)
    unsubmitted = statistics.get('unsubmitted', 0)
    completion_rate = statistics.get('completion_rate', 0)
    
    # 計算進度條寬度 (最大 200px)
    progress_width = int((completion_rate / 100) * 200) if total_students > 0 else 0
    
    # 基本統計內容
    contents = [
        # 標題區塊
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📊 作業統計",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#1DB446"
                },
                {
                    "type": "text",
                    "text": course_name,
                    "size": "md",
                    "color": "#666666",
                    "margin": "xs"
                },
                {
                    "type": "text", 
                    "text": homework_title,
                    "size": "sm",
                    "color": "#999999",
                    "wrap": True,
                    "margin": "xs"
                }
            ],
            "margin": "none",
            "spacing": "sm"
        },
        {
            "type": "separator",
            "margin": "md"
        },
        # 統計數據區塊
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # 完成率進度條
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
                                    "text": f"完成率 {completion_rate}%",
                                    "size": "sm",
                                    "color": "#333333",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": f"{submitted}/{total_students}",
                                    "size": "sm",
                                    "color": "#666666",
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "backgroundColor": "#1DB446",
                                    "height": "6px",
                                    "width": f"{progress_width}px" if progress_width > 0 else "1px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical", 
                                    "contents": [],
                                    "backgroundColor": "#E0E0E0",
                                    "height": "6px",
                                    "flex": 1
                                }
                            ],
                            "margin": "sm"
                        }
                    ]
                },
                # 統計卡片
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "✅",
                                    "size": "lg",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": str(submitted),
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#1DB446",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "已繳交",
                                    "size": "xs",
                                    "color": "#666666",
                                    "align": "center"
                                }
                            ],
                            "backgroundColor": "#F0F9F0",
                            "cornerRadius": "8px",
                            "paddingAll": "12px",
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "❌",
                                    "size": "lg",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": str(unsubmitted),
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FF4444",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "未繳交",
                                    "size": "xs",
                                    "color": "#666666",
                                    "align": "center"
                                }
                            ],
                            "backgroundColor": "#FFF0F0",
                            "cornerRadius": "8px",
                            "paddingAll": "12px",
                            "flex": 1,
                            "margin": "sm"
                        }
                    ],
                    "margin": "md"
                }
            ]
        }
    ]
    
    # 如果有缺交學生，添加名單
    if unsubmitted_students and len(unsubmitted_students) > 0:
        contents.extend([
            {
                "type": "separator",
                "margin": "md"
            },
            {
                "type": "text",
                "text": f"🔍 缺交學生 ({len(unsubmitted_students)}人)",
                "size": "md",
                "weight": "bold",
                "color": "#FF4444",
                "margin": "md"
            }
        ])
        
        # 顯示前5名缺交學生
        for i, student in enumerate(unsubmitted_students[:5]):
            student_name = student.get('name', '未知學生')
            contents.append({
                "type": "text",
                "text": f"• {student_name}",
                "size": "sm",
                "color": "#666666",
                "margin": "xs"
            })
        
        # 如果超過5人，顯示省略提示
        if len(unsubmitted_students) > 5:
            contents.append({
                "type": "text",
                "text": f"... 還有 {len(unsubmitted_students) - 5} 人",
                "size": "sm",
                "color": "#999999",
                "margin": "xs"
            })
    
    # 添加操作按鈕
    button_contents = [
        {
            "type": "separator",
            "margin": "md"
        }
    ]
    
    # 如果有課程和作業ID，添加查看作業按鈕
    if course_id and coursework_id:
        button_contents.append({
            "type": "button",
            "action": {
                "type": "uri",
                "label": "📝 查看作業詳情",
                "uri": create_google_classroom_assignment_url(course_id, coursework_id)
            },
            "style": "secondary",
            "color": "#2196F3",
            "margin": "md"
        })
    
    # 添加通知按鈕
    button_contents.append({
        "type": "button",
        "action": {
            "type": "postback",
            "label": "🔔 自動通知缺交學生",
            "data": f"action=notify_unsubmitted&course_id={course_id or ''}&coursework_id={coursework_id or ''}&homework={homework_title}"
        },
        "style": "primary" if unsubmitted > 0 else "secondary",
        "color": "#FF6B35" if unsubmitted > 0 else "#CCCCCC",
        "margin": "md"
    })
    
    contents.extend(button_contents)
    
    return {
        "type": "flex",
        "altText": f"作業統計 - {homework_title}",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "spacing": "md"
            }
        }
    }

def get_student_homework_status_flex(homeworks: list):
    """
    學生作業狀態 Flex Message - 重新設計的現代化界面
    適用於查看學生所有作業的提交狀況
    
    Args:
        homeworks (list): 作業列表，每個作業應包含以下欄位：
            - course_name: 課程名稱
            - homework_title: 作業標題
            - status: 作業狀態 ("TURNED_IN", "RETURNED", "CREATED", "NOT_FOUND")
            - status_text: 狀態顯示文字
            - is_late: 是否遲交
            - update_time: 更新時間
    """
    # 建立作業項目
    homework_items = []
    
    for i, homework in enumerate(homeworks):
        # 根據狀態選擇顏色和圖示
        status = homework.get("status", "CREATED")
        if status == "TURNED_IN":
            color = "#10B981"  # 綠色 - 已繳交
            icon = "✅"
            bg_color = "#ECFDF5"
        elif status == "RETURNED":
            color = "#3B82F6"  # 藍色 - 已批改
            icon = "📋"
            bg_color = "#EFF6FF"
        elif status == "CREATED":
            color = "#EF4444"  # 紅色 - 未繳交
            icon = "❌"
            bg_color = "#FEF2F2"
        else:
            color = "#6B7280"  # 灰色 - 其他狀態
            icon = "❓"
            bg_color = "#F9FAFB"
        
        # 根據狀態選擇狀態文字
        status_texts = {
            "TURNED_IN": "已繳交",
            "RETURNED": "已批改",
            "CREATED": "未繳交", 
            "NOT_FOUND": "找不到記錄"
        }
        status_text = homework.get("status_text") or status_texts.get(status, "未知狀態")
        
        # 處理遲交標記
        is_late = homework.get("is_late", False)
        if is_late and status == "TURNED_IN":
            status_text += " (遲交)"
        
        # 處理時間格式
        update_time = homework.get("update_time", "")
        if update_time:
            try:
                # 如果是 ISO 格式時間，轉換為可讀格式
                if 'T' in update_time and 'Z' in update_time:
                    from datetime import datetime
                    dt = datetime.fromisoformat(update_time.replace('Z', '+00:00'))
                    update_time = dt.strftime('%Y/%m/%d')
                elif 'T' in update_time and '+' in update_time:
                    from datetime import datetime
                    dt = datetime.fromisoformat(update_time)
                    update_time = dt.strftime('%Y/%m/%d')
            except Exception:
                # 如果轉換失敗，保持原始格式
                pass
        
        homework_item = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # 課程名稱和作業標題
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": homework.get("course_name", "未知課程"),
                            "weight": "bold",
                            "size": "md",
                            "color": "#1F2937",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": homework.get("homework_title", "未知作業"),
                            "size": "sm",
                            "color": "#4B5563",
                            "margin": "xs",
                            "wrap": True
                        }
                    ],
                    "margin": "none"
                },
                # 狀態和時間
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": icon,
                                    "size": "sm",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": status_text,
                                    "size": "sm",
                                    "color": color,
                                    "weight": "bold",
                                    "flex": 1,
                                    "margin": "xs"
                                }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": update_time or "-",
                            "size": "xs",
                            "color": "#9CA3AF",
                            "flex": 0
                        }
                    ],
                    "margin": "sm",
                    "alignItems": "center"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": bg_color,
            "margin": "md" if i == 0 else "sm"
        }
        homework_items.append(homework_item)
    
    # 統計各種狀態的數量
    status_counts = {"TURNED_IN": 0, "RETURNED": 0, "CREATED": 0, "NOT_FOUND": 0}
    for homework in homeworks:
        status = homework.get("status", "NOT_FOUND")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    total_homeworks = len(homeworks)
    completed_count = status_counts["TURNED_IN"] + status_counts["RETURNED"]
    completion_rate = round((completed_count / total_homeworks * 100), 1) if total_homeworks > 0 else 0
    
    # 構建完整的 Flex Message
    contents = [
        # 標題和統計區塊
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📚 作業狀態查詢",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#FFFFFF"
                },
                {
                    "type": "text",
                    "text": f"共 {total_homeworks} 個作業",
                    "size": "sm",
                    "color": "#F3F4F6",
                    "margin": "xs"
                }
            ],
            "backgroundColor": "#4F46E5",
            "paddingAll": "20px"
        },
        # 統計卡片
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        # 完成率
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{completion_rate}%",
                                    "size": "xxl",
                                    "weight": "bold",
                                    "color": "#10B981",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "完成率",
                                    "size": "xs",
                                    "color": "#6B7280",
                                    "align": "center"
                                }
                            ],
                            "flex": 1
                        },
                        # 分隔線
                        {
                            "type": "separator",
                            "color": "#E5E7EB",
                            "margin": "md"
                        },
                        # 已繳交
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(completed_count),
                                    "size": "lg",
                                    "weight": "bold",
                                    "color": "#3B82F6",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "已繳交",
                                    "size": "xs",
                                    "color": "#6B7280",
                                    "align": "center"
                                }
                            ],
                            "flex": 1
                        },
                        # 分隔線
                        {
                            "type": "separator",
                            "color": "#E5E7EB",
                            "margin": "md"
                        },
                        # 未繳交
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(status_counts["CREATED"]),
                                    "size": "lg",
                                    "weight": "bold",
                                    "color": "#EF4444",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "未繳交",
                                    "size": "xs",
                                    "color": "#6B7280",
                                    "align": "center"
                                }
                            ],
                            "flex": 1
                        }
                    ],
                    "paddingAll": "12px",
                    "backgroundColor": "#F9FAFB",
                    "margin": "lg"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF"
        },
        # 作業列表標題
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "📋 作業列表",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#1F2937"
                },
                {
                    "type": "text",
                    "text": f"{len(homeworks)} 項",
                    "size": "sm",
                    "color": "#6B7280"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF"
        },
        # 作業列表
        {
            "type": "box",
            "layout": "vertical",
            "contents": homework_items,
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF"
        },
        # 底部按鈕
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "🔄 重新查詢",
                        "text": "查看作業狀態"
                    },
                    "style": "primary",
                    "color": "#4F46E5",
                    "height": "md"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "🏠 返回主選單",
                        "text": "功能選單"
                    },
                    "style": "secondary",
                    "margin": "sm",
                    "height": "md"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": "#F9FAFB"
        }
    ]
    
    return {
        "type": "flex",
        "altText": f"作業狀態查詢 - 共 {len(homeworks)} 個作業",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "spacing": "none",
                "paddingAll": "0px"
            }
        }
    }
