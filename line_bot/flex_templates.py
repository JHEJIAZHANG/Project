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
                        "spacing": "sm"
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
                        "spacing": "sm"
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
    註冊成功 Flex Message - iOS 風格簡約設計
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
    主功能選單 Flex Message - iOS 風格簡約設計
    包含所有主要功能的入口按鈕
    """
    return {
        "type": "flex",
        "altText": "功能選單",
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
                        "text": "想知道的都在這裡",
                        "weight": "bold",
                        "size": "xxl",
                        "color": "#1C1C1E",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "選擇您需要的功能",
                        "size": "sm",
                        "color": "#8E8E93",
                        "align": "center",
                        "margin": "sm"
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
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "md",
                                "cornerRadius": "16px",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "📚 課程",
                                            "text": "課程管理"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
                                    },
                                    {
                                        "type": "button", 
                                        "action": {
                                            "type": "message",
                                            "label": "📝 作業",
                                            "text": "作業管理"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal", 
                                "spacing": "md",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "📅 行事曆",
                                            "text": "行事曆管理"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
                                    },
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "📓 筆記",
                                            "text": "筆記管理"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "md",
                                "cornerRadius": "16px", 
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "⚙️ 設定",
                                            "text": "帳戶設定"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
                                    },
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "❓ 說明",
                                            "text": "使用說明"
                                        },
                                                                        "style": "secondary",
                                "height": "md",
                                "color": "#F2F2F7",
                                "cornerRadius": "18px"
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
    課程管理功能選單 - iOS 風格簡約設計
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
                                    "label": "⚙️ 課程設定",
                                    "text": "管理課程設定"
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
    作業管理功能選單 - iOS 風格簡約設計
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
    行事曆管理功能選單 - iOS 風格簡約設計
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
    筆記管理功能選單 - iOS 風格簡約設計
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
    帳戶設定功能選單 - iOS 風格簡約設計
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
                                "text": "在聊天室記或直接輸入【預算】",
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
                                "text": "都可以查看預算餘額",
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
                                "text": "預算比例功能讓財務管理更輕鬆！",
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
                                "text": "文字/語音輸入【備註+金額】",
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
                                        "text": "小笨蛋晚餐費",
                                        "size": "xs",
                                        "color": "#4CAF50",
                                        "backgroundColor": "#E8F5E8",
                                        "paddingAll": "4px"
                                    },
                                    {
                                        "type": "text",
                                        "text": "$888",
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
                                "text": "也可指定【日期】&【帳本】&【類型】",
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
                                "text": "送出後會顯示記帳確認訊息",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "$888...",
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
                                "text": "可點選【編輯】做文字內容修改",
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
                                "text": "點擊右側新增錢包頁面",
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
                                "text": "輸入金額按後設定該【新增】",
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
                                "text": "記帳後會跳出三個按鈕，點【明細】",
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
                                "text": "本月統計\n預算比例\n明細收支",
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
                                "text": "本月統計",
                                "size": "sm",
                                "color": "#333333",
                                "wrap": True,
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "9567",
                                "size": "xl",
                                "color": "#4CAF50",
                                "weight": "bold",
                                "align": "center",
                                "margin": "sm"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "預算比例",
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
                                "text": "可以在【記帳格式】中更下列功能",
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
                                "text": "預設 1\n實用末端功能表",
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
        
        # 課程刪除確認模板
        "course_deletion_confirmation": get_course_deletion_confirmation_flex(kwargs.get('courses', [])),
        "course_deletion_confirmation_paginated": get_course_deletion_confirmation_paginated_flex(
            kwargs.get('courses', []), 
            kwargs.get('page_size', 8)
        ),
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
        
        # 課程刪除確認模板
        "course_deletion_confirmation",
        "course_deletion_confirmation_paginated",
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
            "course_deletion_confirmation",
            "course_deletion_confirmation_paginated"
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
