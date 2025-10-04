#!/usr/bin/env python3
"""
測試 Google Classroom 課程匯入時不自動設定預設時間
"""
import os
import sys
import django

# 設定 Django 環境
sys.path.append('/Users/jhejia/Desktop/ntub v2 3/ntub v2 2/ntub v2/classroomai')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classroomai.settings')
django.setup()

from api_v2.models import CourseV2, CourseScheduleV2
from services.classroom_sync_service import ClassroomSyncService

def test_no_default_schedule():
    """測試 Google Classroom 課程匯入時不會自動設定預設時間"""
    
    print("=== 測試 Google Classroom 課程匯入不設定預設時間 ===\n")
    
    # 使用真實的 LINE 使用者 ID
    line_user_id = "U015b486e04b09ae70bde24db70ec9611"
    
    try:
        # 1. 檢查匯入前的課程狀態
        print("1. 檢查匯入前的課程時間設定:")
        google_courses = CourseV2.objects.filter(
            user__line_user_id=line_user_id,
            is_google_classroom=True
        )[:3]
        
        for course in google_courses:
            schedules = course.schedules.all()
            default_schedules = course.schedules.filter(is_default_schedule=True)
            print(f"   課程: {course.title}")
            print(f"   總時間設定數: {schedules.count()}")
            print(f"   預設時間設定數: {default_schedules.count()}")
            if default_schedules.exists():
                for schedule in default_schedules:
                    print(f"     - {schedule.get_day_of_week_display()} {schedule.start_time}-{schedule.end_time}")
            print()
        
        # 2. 刪除現有的預設時間設定（模擬重新匯入）
        print("2. 清除現有預設時間設定...")
        CourseScheduleV2.objects.filter(
            course__user__line_user_id=line_user_id,
            course__is_google_classroom=True,
            is_default_schedule=True
        ).delete()
        
        # 3. 執行同步
        print("3. 執行 Google Classroom 同步...")
        sync_service = ClassroomSyncService(line_user_id)
        result = sync_service.sync_all_courses()
        
        print(f"   同步結果: {'成功' if result['success'] else '失敗'}")
        print(f"   同步課程數: {result['courses_synced']}")
        if result['errors']:
            print(f"   錯誤: {result['errors']}")
        print()
        
        # 4. 檢查匯入後的課程狀態
        print("4. 檢查匯入後的課程時間設定:")
        google_courses = CourseV2.objects.filter(
            user__line_user_id=line_user_id,
            is_google_classroom=True
        )[:3]
        
        has_default_schedules = False
        for course in google_courses:
            schedules = course.schedules.all()
            default_schedules = course.schedules.filter(is_default_schedule=True)
            print(f"   課程: {course.title}")
            print(f"   總時間設定數: {schedules.count()}")
            print(f"   預設時間設定數: {default_schedules.count()}")
            if default_schedules.exists():
                has_default_schedules = True
                for schedule in default_schedules:
                    print(f"     - {schedule.get_day_of_week_display()} {schedule.start_time}-{schedule.end_time}")
            print()
        
        # 5. 驗證結果
        print("5. 測試結果:")
        if has_default_schedules:
            print("   ❌ 測試失敗：仍然有預設時間設定被創建")
        else:
            print("   ✅ 測試成功：沒有自動創建預設時間設定")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_default_schedule()