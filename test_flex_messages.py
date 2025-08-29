#!/usr/bin/env python
"""
Flex Message 測試腳本
執行方式: python test_flex_messages.py
"""

import os
import sys
import django
import json

# 設定 Django 環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classroomai.settings')
django.setup()

from line_bot.flex_templates import (
    get_teacher_homework_statistics_flex,
    get_student_homework_status_flex,
    get_flex_template
)

def test_teacher_statistics():
    """測試教師統計 Flex Message"""
    print("=== 測試教師統計 Flex Message ===")
    
    # 模擬統計數據
    statistics = {
        'total_students': 25,
        'submitted': 18,
        'unsubmitted': 7,
        'completion_rate': 72.0
    }
    
    # 模擬缺交學生
    unsubmitted_students = [
        {'name': '王小明'},
        {'name': '李小華'},
        {'name': '張小美'},
        {'name': '陳小強'},
        {'name': '林小雯'},
        {'name': '黃小龍'}
    ]
    
    try:
        flex_message = get_teacher_homework_statistics_flex(
            course_name="資料結構與演算法",
            homework_title="二元樹實作作業",
            statistics=statistics,
            unsubmitted_students=unsubmitted_students
        )
        
        print("✅ 教師統計 Flex Message 生成成功")
        print(f"📱 Alt Text: {flex_message['altText']}")
        
        # 保存為 JSON 檔案
        with open('teacher_statistics_flex.json', 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)
        print("💾 已保存到 teacher_statistics_flex.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_student_status():
    """測試學生狀態 Flex Message"""
    print("\n=== 測試學生狀態 Flex Message ===")
    
    # 測試未繳交狀態
    status_info = {
        'status': 'CREATED',
        'is_late': False,
        'update_time': '2024-08-29 10:00:00'
    }
    
    unsubmitted_homeworks = [
        "二元樹實作作業",
        "排序演算法分析",
        "圖論應用題目"
    ]
    
    try:
        flex_message = get_student_homework_status_flex(
            course_name="資料結構與演算法",
            homework_title="二元樹實作作業",
            status_info=status_info,
            unsubmitted_homeworks=unsubmitted_homeworks
        )
        
        print("✅ 學生狀態 Flex Message 生成成功")
        print(f"📱 Alt Text: {flex_message['altText']}")
        
        # 保存為 JSON 檔案
        with open('student_status_flex.json', 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)
        print("💾 已保存到 student_status_flex.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_template_integration():
    """測試模板整合"""
    print("\n=== 測試模板整合 ===")
    
    try:
        # 測試透過 get_flex_template 調用
        teacher_template = get_flex_template(
            'teacher_homework_statistics',
            course_name="測試課程",
            homework_title="測試作業",
            statistics={'total_students': 10, 'submitted': 7, 'unsubmitted': 3, 'completion_rate': 70.0},
            unsubmitted_students=[{'name': '測試學生'}]
        )
        
        if teacher_template:
            print("✅ 教師統計模板整合成功")
        
        student_template = get_flex_template(
            'student_homework_status',
            course_name="測試課程",
            homework_title="測試作業",
            status_info={'status': 'CREATED', 'is_late': False, 'update_time': '2024-08-29'},
            unsubmitted_homeworks=['作業1', '作業2']
        )
        
        if student_template:
            print("✅ 學生狀態模板整合成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模板整合測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始執行 Flex Message 測試")
    print("=" * 50)
    
    tests = [
        test_teacher_statistics,
        test_student_status,
        test_template_integration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 測試結果: {passed}/{len(tests)} 通過")
    
    if passed == len(tests):
        print("🎉 所有測試通過!")
        print("\n📂 生成的檔案:")
        print("- teacher_statistics_flex.json (教師統計Flex)")
        print("- student_status_flex.json (學生狀態Flex)")
        print("\n💡 您可以將這些JSON檔案貼到LINE Flex Message Simulator查看效果")
        print("🔗 https://developers.line.biz/flex-simulator/")
    else:
        print("⚠️  部分測試失敗，請檢查錯誤訊息")