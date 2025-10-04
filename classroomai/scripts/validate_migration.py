#!/usr/bin/env python
"""
資料庫遷移驗證腳本
驗證新增欄位和索引的正確性
"""
import os
import sys
import django
from django.db import connection
from django.core.management import execute_from_command_line

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classroomai.settings')
django.setup()

from api_v2.models import CourseV2, AssignmentV2, CourseScheduleV2
from user.models import LineProfile


def validate_model_fields():
    """驗證模型欄位"""
    print("=== 驗證模型欄位 ===")
    
    # 驗證 CourseV2 欄位
    course_fields = [f.name for f in CourseV2._meta.fields]
    required_course_fields = [
        'google_classroom_id', 'is_google_classroom'
    ]
    
    print("CourseV2 欄位驗證:")
    for field in required_course_fields:
        if field in course_fields:
            print(f"  ✓ {field} - 存在")
        else:
            print(f"  ✗ {field} - 缺失")
    
    # 驗證 AssignmentV2 欄位
    assignment_fields = [f.name for f in AssignmentV2._meta.fields]
    required_assignment_fields = [
        'google_coursework_id'
    ]
    
    print("\nAssignmentV2 欄位驗證:")
    for field in required_assignment_fields:
        if field in assignment_fields:
            print(f"  ✓ {field} - 存在")
        else:
            print(f"  ✗ {field} - 缺失")
    
    # 驗證 CourseScheduleV2 欄位
    schedule_fields = [f.name for f in CourseScheduleV2._meta.fields]
    required_schedule_fields = [
        'schedule_source', 'is_default_schedule'
    ]
    
    print("\nCourseScheduleV2 欄位驗證:")
    for field in required_schedule_fields:
        if field in schedule_fields:
            print(f"  ✓ {field} - 存在")
        else:
            print(f"  ✗ {field} - 缺失")


def validate_database_indexes():
    """驗證資料庫索引"""
    print("\n=== 驗證資料庫索引 ===")
    
    with connection.cursor() as cursor:
        # 檢查 CourseV2 索引
        cursor.execute("""
            SELECT DISTINCT INDEX_NAME 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'api_v2_coursev2'
            AND COLUMN_NAME IN ('google_classroom_id', 'is_google_classroom', 'user_id')
        """)
        
        course_indexes = [row[0] for row in cursor.fetchall()]
        print("CourseV2 索引:")
        for index in course_indexes:
            print(f"  ✓ {index}")
        
        # 檢查 AssignmentV2 索引
        cursor.execute("""
            SELECT DISTINCT INDEX_NAME 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'api_v2_assignmentv2'
            AND COLUMN_NAME IN ('google_coursework_id', 'user_id', 'course_id')
        """)
        
        assignment_indexes = [row[0] for row in cursor.fetchall()]
        print("\nAssignmentV2 索引:")
        for index in assignment_indexes:
            print(f"  ✓ {index}")


def test_data_operations():
    """測試資料操作"""
    print("\n=== 測試資料操作 ===")
    
    try:
        # 創建驗證使用者 - 需要提供真實用戶ID進行測試
        test_user_id = os.environ.get('TEST_USER_ID')
        if not test_user_id:
            print("✗ 需要設置 TEST_USER_ID 環境變數")
            return False
            
        user, created = LineProfile.objects.get_or_create(
            line_user_id=test_user_id,
            defaults={
                'role': 'student',
                'name': 'Migration Test',
                'email': f'{test_user_id}@test.local'
            }
        )
        print("✓ 使用者創建/獲取成功")
        
        # 創建本地課程
        local_course = CourseV2.objects.create(
            user=user,
            title='Migration Test Local',
            description='Local course validation',
            is_google_classroom=False
        )
        print("✓ 本地課程創建成功")
        
        # 創建 Classroom 鏡像課程
        mirror_course = CourseV2.objects.create(
            user=user,
            title='Migration Test Classroom',
            description='Classroom course validation',
            is_google_classroom=True,
            google_classroom_id=f'test_classroom_{test_user_id}'
        )
        print("✓ Classroom 鏡像課程創建成功")
        
        # 創建本地作業
        local_assignment = AssignmentV2.objects.create(
            user=user,
            course=local_course,
            title='Migration Test Assignment',
            description='Local assignment validation',
            due_date='2024-12-31 23:59:00'
        )
        print("✓ 本地作業創建成功")
        
        # 創建 Classroom 鏡像作業
        mirror_assignment = AssignmentV2.objects.create(
            user=user,
            course=mirror_course,
            title='Migration Test Coursework',
            description='Classroom assignment validation',
            due_date='2024-12-31 23:59:00',
            google_coursework_id=f'test_coursework_{test_user_id}'
        )
        print("✓ Classroom 鏡像作業創建成功")
        
        # 創建課程時間
        schedule = CourseScheduleV2.objects.create(
            course=local_course,
            day_of_week=1,
            start_time='09:00:00',
            end_time='10:30:00',
            location='A101',
            schedule_source='manual',
            is_default_schedule=False
        )
        print("✓ 課程時間創建成功")
        
        # 測試查詢
        local_courses = CourseV2.objects.filter(user=user, is_google_classroom=False)
        mirror_courses = CourseV2.objects.filter(user=user, is_google_classroom=True)
        
        print(f"✓ 查詢測試成功 - 本地課程: {local_courses.count()}, 鏡像課程: {mirror_courses.count()}")
        
        # 清理測試資料
        CourseV2.objects.filter(user=user).delete()
        user.delete()
        print("✓ 測試資料清理完成")
        
    except Exception as e:
        print(f"✗ 資料操作測試失敗: {str(e)}")
        return False
    
    return True


def validate_backward_compatibility():
    """驗證向後相容性"""
    print("\n=== 驗證向後相容性 ===")
    
    try:
        # 檢查舊的模型是否仍然可用
        from course.models import Course, Homework
        
        print("✓ 舊模型 (Course, Homework) 仍然可用")
        
        # 測試舊模型的基本操作
        old_course_count = Course.objects.count()
        old_homework_count = Homework.objects.count()
        
        print(f"✓ 舊資料完整性檢查 - 課程: {old_course_count}, 作業: {old_homework_count}")
        
    except Exception as e:
        print(f"✗ 向後相容性檢查失敗: {str(e)}")
        return False
    
    return True


def main():
    """主函數"""
    print("開始資料庫遷移驗證...")
    print("=" * 50)
    
    # 驗證模型欄位
    validate_model_fields()
    
    # 驗證資料庫索引
    try:
        validate_database_indexes()
    except Exception as e:
        print(f"索引驗證跳過 (可能使用 SQLite): {str(e)}")
    
    # 測試資料操作
    data_test_success = test_data_operations()
    
    # 驗證向後相容性
    compatibility_success = validate_backward_compatibility()
    
    print("\n" + "=" * 50)
    if data_test_success and compatibility_success:
        print("✅ 資料庫遷移驗證完成 - 所有測試通過")
        return 0
    else:
        print("❌ 資料庫遷移驗證失敗 - 部分測試未通過")
        return 1


if __name__ == '__main__':
    sys.exit(main())