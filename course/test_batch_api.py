#!/usr/bin/env python3
"""
測試批量作業提交狀態查詢 API 的腳本
展示如何使用新的批量查詢功能（包含 Flex Message 發送）
"""

import json

# API 端點
API_URL = "http://localhost:8000/api/classroom/submissions/status"

# 測試用的 LINE 用戶 ID（請替換為實際的 ID）
LINE_USER_ID = "U1234567890abcdef"

def test_batch_query_method1():
    """測試批量查詢模式 - 方法一：使用 course_coursework_pairs"""
    print("=== 測試批量查詢模式 - 方法一 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "course_id_1",
                "coursework_id": "coursework_id_1"
            },
            {
                "course_id": "course_id_2",
                "coursework_id": "coursework_id_2"
            },
            {
                "course_id": "course_id_3",
                "coursework_id": "coursework_id_3"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 包含 3 個課程作業狀態的批量結果")
    print("教師查詢會自動發送 Flex Message 到 LINE")
    print()

def test_batch_query_method2():
    """測試批量查詢模式 - 方法二：使用 course_ids + coursework_ids"""
    print("=== 測試批量查詢模式 - 方法二 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_ids": ["course_id_1", "course_id_2", "course_id_3"],
        "coursework_ids": ["coursework_id_1", "coursework_id_2", "coursework_id_3"]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 包含 3 個課程作業狀態的批量結果")
    print("教師查詢會自動發送 Flex Message 到 LINE")
    print()

def test_single_course_multiple_homeworks():
    """測試單一課程多作業查詢"""
    print("=== 測試單一課程多作業查詢 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "python_course_2024",
                "coursework_id": "hw1_basic_syntax"
            },
            {
                "course_id": "python_course_2024",
                "coursework_id": "hw2_functions"
            },
            {
                "course_id": "python_course_2024",
                "coursework_id": "hw3_oop"
            },
            {
                "course_id": "python_course_2024",
                "coursework_id": "final_project"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 單一課程的 4 個作業狀態")
    print("教師會收到 4 個 Flex Message 統計圖表")
    print()

def test_single_course_single_homework():
    """測試單一課程單作業查詢（使用批量查詢格式）"""
    print("=== 測試單一課程單作業查詢 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "python_course_2024",
                "coursework_id": "hw1_basic_syntax"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 單一課程作業的狀態")
    print("教師會收到 1 個 Flex Message 統計圖表")
    print()

def test_mixed_roles():
    """測試混合角色查詢（教師和學生）"""
    print("=== 測試混合角色查詢 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "teacher_course_id",      # 用戶是教師的課程
                "coursework_id": "teacher_homework_id"
            },
            {
                "course_id": "student_course_id",      # 用戶是學生的課程
                "coursework_id": "student_homework_id"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 第一個課程回傳教師統計，第二個課程回傳學生狀態")
    print("教師查詢會發送 Flex Message，學生查詢不會")
    print()

def test_error_handling():
    """測試錯誤處理"""
    print("=== 測試錯誤處理 ===")
    
    # 測試無效的課程 ID
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "invalid_course_id",
                "coursework_id": "invalid_coursework_id"
            },
            {
                "course_id": "valid_course_id",
                "coursework_id": "valid_coursework_id"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 第一個查詢失敗，第二個查詢成功")
    print("錯誤查詢不會影響成功查詢的結果")
    print("成功的教師查詢仍會發送 Flex Message")
    print()

def test_validation():
    """測試參數驗證"""
    print("=== 測試參數驗證 ===")
    
    # 測試缺少必要參數
    invalid_data = {
        "line_user_id": LINE_USER_ID
        # 缺少 course_coursework_pairs
    }
    
    print(f"無效請求資料: {json.dumps(invalid_data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 驗證錯誤，提示缺少必要參數")
    print()
    
    # 測試數量不匹配
    invalid_data2 = {
        "line_user_id": LINE_USER_ID,
        "course_ids": ["course_id_1", "course_id_2"],
        "coursework_ids": ["coursework_id_1"]  # 數量不匹配
    }
    
    print(f"無效請求資料: {json.dumps(invalid_data2, indent=2, ensure_ascii=False)}")
    print("預期回傳: 驗證錯誤，提示 course_ids 和 coursework_ids 數量必須相同")
    print()

def test_flex_message_features():
    """測試 Flex Message 功能"""
    print("=== 測試 Flex Message 功能 ===")
    
    data = {
        "line_user_id": LINE_USER_ID,
        "course_coursework_pairs": [
            {
                "course_id": "teacher_course_1",
                "coursework_id": "homework_1"
            },
            {
                "course_id": "teacher_course_2",
                "coursework_id": "homework_2"
            }
        ]
    }
    
    print(f"請求資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("預期回傳: 包含 flex_messages_sent 欄位")
    print("教師會收到 2 個 Flex Message 統計圖表")
    print("回傳結果會顯示發送狀態")
    print()

def main():
    """主函數"""
    print("批量作業提交狀態查詢 API 測試腳本（含 Flex Message 功能）")
    print("=" * 60)
    print()
    
    # 執行各種測試
    test_batch_query_method1()
    test_batch_query_method2()
    test_single_course_multiple_homeworks()
    test_single_course_single_homework()
    test_mixed_roles()
    test_error_handling()
    test_validation()
    test_flex_message_features()
    
    print("=" * 60)
    print("測試腳本執行完成！")
    print()
    print("主要改進:")
    print("✅ 移除單一查詢模式，統一使用批量查詢")
    print("✅ 教師查詢自動發送 Flex Message 到 LINE")
    print("✅ 支援單一課程單作業查詢（使用批量格式）")
    print("✅ 支援單一課程多作業查詢")
    print("✅ 支援多課程多作業查詢")
    print("✅ 智能角色辨識和錯誤處理")
    print()
    print("使用說明:")
    print("1. 將 LINE_USER_ID 替換為實際的用戶 ID")
    print("2. 將課程和作業 ID 替換為實際的 ID")
    print("3. 確保 Django 服務器正在運行")
    print("4. 使用 POST 方法呼叫 API")
    print("5. 教師查詢會自動發送 Flex Message")
    print()
    print("API 端點: POST " + API_URL)
    print("支援 GET 和 POST 方法")

if __name__ == "__main__":
    main()
