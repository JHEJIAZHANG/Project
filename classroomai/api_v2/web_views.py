"""
網頁資料 CRUD API 視圖
處理 LIFF 網頁端的本地資料操作
"""
import logging
from datetime import datetime, time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from user.models import LineProfile
from api_v2.models import CourseScheduleV2
from services.web_data_service import WebDataService, WebDataError, PermissionDeniedError

logger = logging.getLogger(__name__)


def _parse_time_string(time_str: str) -> time:
    """解析時間字串為 time 物件"""
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            raise ValueError(f"無效的時間格式: {time_str}")


def _parse_datetime_string(datetime_str: str) -> datetime:
    """解析日期時間字串為 datetime 物件"""
    try:
        # 嘗試 ISO 格式
        return timezone.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # 嘗試其他格式
            return timezone.make_aware(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            raise ValueError(f"無效的日期時間格式: {datetime_str}")


# ==================== 課程相關 API ====================

@api_view(["POST"])
@permission_classes([AllowAny])
def create_course(request):
    """
    創建本地課程
    
    POST /api/web/courses/create/
    {
        "line_user_id": "U123456789",
        "title": "我的自訂課程",
        "description": "課程描述",
        "instructor": "講師名稱",
        "classroom": "教室位置",
        "color": "#8b5cf6"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        title = request.data.get('title')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not title:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 title 參數",
                "code": "MISSING_TITLE"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 準備課程資料
        course_data = {
            'title': title,
            'description': request.data.get('description', ''),
            'instructor': request.data.get('instructor', ''),
            'classroom': request.data.get('classroom', ''),
            'color': request.data.get('color', '#8b5cf6')
        }
        
        # 創建課程
        course = WebDataService.create_local_course(user, **course_data)
        
        # 處理時間表數據
        schedules = request.data.get('schedules', [])
        if schedules:
            try:
                # 創建課程時間表
                for schedule_data in schedules:
                    day_of_week = schedule_data.get('day_of_week')
                    start_time = schedule_data.get('start_time')
                    end_time = schedule_data.get('end_time')
                    
                    if day_of_week is not None and start_time and end_time:
                        # 解析時間字符串
                        start_time_obj = _parse_time_string(start_time)
                        end_time_obj = _parse_time_string(end_time)
                        
                        CourseScheduleV2.objects.create(
                            course=course,
                            day_of_week=day_of_week,
                            start_time=start_time_obj,
                            end_time=end_time_obj,
                            location=course.classroom or '',
                            schedule_source='manual',
                            is_default_schedule=False
                        )
                        
                logger.info(f"Created {len(schedules)} schedules for course: {course.title}")
            except Exception as e:
                logger.error(f"Error creating schedules for course {course.id}: {str(e)}")
                # 不要因為時間表創建失敗而回滾整個課程創建
        
        logger.info(f"Created course via API: {course.title} for user: {line_user_id}")
        
        # 獲取創建的時間表數據以返回完整信息
        schedules_data = []
        for schedule in course.schedules.all():
            schedules_data.append({
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.strftime('%H:%M'),
                "end_time": schedule.end_time.strftime('%H:%M'),
                "location": schedule.location
            })
        
        return Response({
            "success": True,
            "message": "課程創建成功",
            "data": {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "instructor": course.instructor,
                "classroom": course.classroom,
                "color": course.color,
                "is_google_classroom": course.is_google_classroom,
                "created_at": course.created_at.isoformat(),
                "schedules": schedules_data
            }
        }, status=status.HTTP_201_CREATED)
    
    except WebDataError as e:
        logger.error(f"WebData error creating course: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error creating course: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "創建課程時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_course(request):
    """
    更新本地課程
    
    PATCH /api/web/courses/update/
    {
        "line_user_id": "U123456789",
        "course_id": "uuid",
        "title": "更新後的課程名稱"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        course_id = request.data.get('course_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 course_id 參數",
                "code": "MISSING_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 獲取課程物件
        from api_v2.models import CourseV2
        course = get_object_or_404(CourseV2, id=course_id)
        
        # 檢查權限
        WebDataService._validate_user_permission(user, course)
        
        # 準備更新資料
        update_data = {}
        for field in ['title', 'description', 'instructor', 'classroom', 'color']:
            if field in request.data:
                update_data[field] = request.data[field]
        
        # 處理 schedules 資料
        schedules_data = request.data.get('schedules')
        
        if not update_data and not schedules_data:
            return Response({
                "error": "missing_data",
                "message": "沒有提供要更新的資料",
                "code": "NO_UPDATE_DATA"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 智能處理 Google Classroom 課程的更新請求
        if course.is_google_classroom:
            # 對於 Google Classroom 課程，只允許更新時間表
            if update_data and not schedules_data:
                # 如果只有基本資料更新，直接拒絕
                return Response({
                    "error": "classroom_data_protected",
                    "message": "無法修改 Google Classroom 同步的課程資料",
                    "code": "CLASSROOM_DATA_PROTECTED"
                }, status=status.HTTP_400_BAD_REQUEST)
            elif update_data and schedules_data:
                # 如果同時有基本資料和時間表更新，只處理時間表，忽略基本資料
                logger.info(f"Ignoring basic data updates for Google Classroom course {course_id}, only updating schedule")
                update_data = {}  # 清空基本資料更新
        
        # 更新課程基本資料（如果有的話且不是 Google Classroom 課程）
        if update_data:
            course = WebDataService.update_local_course(user, course_id, **update_data)
        
        # 如果有 schedules 資料，更新課程時間表（允許 Google Classroom 課程更新時間）
        if schedules_data:
            # 使用 WebDataService 的 update_course_schedule 方法
            WebDataService.update_course_schedule(user, course_id, [
                {
                    'day_of_week': schedule.get('day_of_week'),
                    'start_time': _parse_time_string(schedule.get('start_time')),
                    'end_time': _parse_time_string(schedule.get('end_time')),
                    'location': schedule.get('location', '')
                }
                for schedule in schedules_data
            ])
        
        logger.info(f"Updated course via API: {course.title} for user: {line_user_id}")
        
        return Response({
            "success": True,
            "message": "課程更新成功",
            "data": {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "instructor": course.instructor,
                "classroom": course.classroom,
                "color": course.color,
                "is_google_classroom": course.is_google_classroom,
                "updated_at": course.updated_at.isoformat()
            }
        }, status=status.HTTP_200_OK)
    
    except PermissionDeniedError as e:
        logger.warning(f"Permission denied updating course: {str(e)}")
        return Response({
            "error": "permission_denied",
            "message": str(e),
            "code": "CLASSROOM_DATA_READONLY" if "Google Classroom" in str(e) else "PERMISSION_DENIED"
        }, status=status.HTTP_403_FORBIDDEN)
    
    except WebDataError as e:
        logger.error(f"WebData error updating course: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error updating course: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "更新課程時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_course(request):
    """
    刪除本地課程
    
    DELETE /api/web/courses/delete/
    {
        "line_user_id": "U123456789",
        "course_id": "uuid"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        course_id = request.data.get('course_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 course_id 參數",
                "code": "MISSING_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 刪除課程
        success = WebDataService.delete_local_course(user, course_id)
        
        if success:
            logger.info(f"Deleted course via API: {course_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "課程刪除成功"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "delete_failed",
                "message": "刪除課程失敗",
                "code": "DELETE_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except PermissionDeniedError as e:
        logger.warning(f"Permission denied deleting course: {str(e)}")
        return Response({
            "error": "permission_denied",
            "message": str(e),
            "code": "CLASSROOM_DATA_READONLY" if "Google Classroom" in str(e) else "PERMISSION_DENIED"
        }, status=status.HTTP_403_FORBIDDEN)
    
    except WebDataError as e:
        logger.error(f"WebData error deleting course: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error deleting course: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "刪除課程時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_courses(request):
    """
    查詢課程列表
    
    GET /api/web/courses/list/?line_user_id=U123456789
    """
    try:
        # 驗證必要參數
        line_user_id = request.GET.get('line_user_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 獲取課程列表
        courses = WebDataService.get_integrated_courses(user)
        
        logger.info(f"Retrieved {len(courses)} courses via API for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": {
                "courses": courses,
                "total": len(courses)
            }
        }, status=status.HTTP_200_OK)
    
    except WebDataError as e:
        logger.error(f"WebData error listing courses: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error listing courses: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取課程列表時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def set_course_schedule(request):
    """
    設定課程時間（包含 Classroom 鏡像課程）
    
    POST /api/web/courses/schedule/
    {
        "line_user_id": "U123456789",
        "course_id": "uuid",
        "schedules": [
            {
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "10:30:00",
                "location": "A101 教室"
            }
        ]
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        course_id = request.data.get('course_id')
        schedules = request.data.get('schedules', [])
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 course_id 參數",
                "code": "MISSING_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not schedules:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 schedules 參數",
                "code": "MISSING_SCHEDULES"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 驗證和轉換時間格式
        processed_schedules = []
        for schedule in schedules:
            try:
                processed_schedule = {
                    'day_of_week': int(schedule['day_of_week']),
                    'start_time': _parse_time_string(schedule['start_time']),
                    'end_time': _parse_time_string(schedule['end_time']),
                    'location': schedule.get('location', '')
                }
                
                # 驗證星期幾的範圍
                if not 0 <= processed_schedule['day_of_week'] <= 6:
                    raise ValueError("day_of_week 必須在 0-6 之間")
                
                # 驗證時間邏輯
                if processed_schedule['start_time'] >= processed_schedule['end_time']:
                    raise ValueError("開始時間必須早於結束時間")
                
                processed_schedules.append(processed_schedule)
                
            except (KeyError, ValueError, TypeError) as e:
                return Response({
                    "error": "invalid_schedule",
                    "message": f"時間設定格式錯誤: {str(e)}",
                    "code": "INVALID_SCHEDULE_FORMAT"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新課程時間
        success = WebDataService.update_course_schedule(user, course_id, processed_schedules)
        
        if success:
            logger.info(f"Updated course schedule via API: {course_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "課程時間設定成功",
                "data": {
                    "course_id": course_id,
                    "schedules_count": len(processed_schedules)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "update_failed",
                "message": "更新課程時間失敗",
                "code": "UPDATE_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except WebDataError as e:
        logger.error(f"WebData error setting course schedule: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error setting course schedule: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "設定課程時間時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ================= 作業相關 API ====================

@api_view(["POST"])
@permission_classes([AllowAny])
def create_assignment(request):
    """
    創建本地作業
    
    POST /api/web/assignments/create/
    {
        "line_user_id": "U123456789",
        "course_id": "uuid",
        "title": "作業標題",
        "due_date": "2024-09-30T23:59:59Z",
        "description": "作業描述",
        "status": "pending",
        "type": "assignment"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        course_id = request.data.get('course_id')
        title = request.data.get('title')
        due_date_str = request.data.get('due_date')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 course_id 參數",
                "code": "MISSING_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not title:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 title 參數",
                "code": "MISSING_TITLE"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not due_date_str:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 due_date 參數",
                "code": "MISSING_DUE_DATE"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 解析截止日期
        try:
            due_date = _parse_datetime_string(due_date_str)
        except ValueError as e:
            return Response({
                "error": "invalid_date",
                "message": str(e),
                "code": "INVALID_DATE_FORMAT"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 準備作業資料
        assignment_data = {
            'course_id': course_id,
            'title': title,
            'due_date': due_date,
            'description': request.data.get('description', ''),
            'status': request.data.get('status', 'pending'),
            'type': request.data.get('type', 'assignment')
        }
        
        # 創建作業
        assignment = WebDataService.create_local_assignment(user, **assignment_data)
        
        logger.info(f"Created assignment via API: {assignment.title} for user: {line_user_id}")
        
        return Response({
            "success": True,
            "message": "作業創建成功",
            "data": {
                "id": str(assignment.id),
                "title": assignment.title,
                "description": assignment.description,
                "due_date": assignment.due_date.isoformat(),
                "type": assignment.type,
                "status": assignment.status,
                "course": {
                    "id": str(assignment.course.id),
                    "title": assignment.course.title
                },
                "is_google_classroom": assignment.is_google_classroom,
                "created_at": assignment.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    
    except WebDataError as e:
        logger.error(f"WebData error creating assignment: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error creating assignment: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "創建作業時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_assignment(request):
    """
    更新本地作業
    
    PATCH /api/web/assignments/update/
    {
        "line_user_id": "U123456789",
        "assignment_id": "uuid",
        "due_date": "2024-10-15T23:59:59Z"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        assignment_id = request.data.get('assignment_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not assignment_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 assignment_id 參數",
                "code": "MISSING_ASSIGNMENT_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 準備更新資料
        update_data = {}
        for field in ['title', 'description', 'status', 'type', 'course_id']:
            if field in request.data:
                update_data[field] = request.data[field]
        
        # 處理截止日期
        if 'due_date' in request.data:
            try:
                update_data['due_date'] = _parse_datetime_string(request.data['due_date'])
            except ValueError as e:
                return Response({
                    "error": "invalid_date",
                    "message": str(e),
                    "code": "INVALID_DATE_FORMAT"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if not update_data:
            return Response({
                "error": "missing_data",
                "message": "沒有提供要更新的資料",
                "code": "NO_UPDATE_DATA"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新作業
        assignment = WebDataService.update_local_assignment(user, assignment_id, **update_data)
        
        logger.info(f"Updated assignment via API: {assignment.title} for user: {line_user_id}")
        
        return Response({
            "success": True,
            "message": "作業更新成功",
            "data": {
                "id": str(assignment.id),
                "title": assignment.title,
                "description": assignment.description,
                "due_date": assignment.due_date.isoformat(),
                "type": assignment.type,
                "status": assignment.status,
                "course": {
                    "id": str(assignment.course.id),
                    "title": assignment.course.title
                },
                "is_google_classroom": assignment.is_google_classroom,
                "updated_at": assignment.updated_at.isoformat()
            }
        }, status=status.HTTP_200_OK)
    
    except PermissionDeniedError as e:
        logger.warning(f"Permission denied updating assignment: {str(e)}")
        return Response({
            "error": "permission_denied",
            "message": str(e),
            "code": "CLASSROOM_DATA_READONLY" if "Google Classroom" in str(e) else "PERMISSION_DENIED"
        }, status=status.HTTP_403_FORBIDDEN)
    
    except WebDataError as e:
        logger.error(f"WebData error updating assignment: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error updating assignment: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "更新作業時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_assignment(request):
    """
    刪除本地作業
    
    DELETE /api/web/assignments/delete/
    {
        "line_user_id": "U123456789",
        "assignment_id": "uuid"
    }
    """
    try:
        # 驗證必要參數
        line_user_id = request.data.get('line_user_id')
        assignment_id = request.data.get('assignment_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not assignment_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 assignment_id 參數",
                "code": "MISSING_ASSIGNMENT_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 直接刪除作業
        from .models import AssignmentV2
        try:
            assignment = AssignmentV2.objects.get(id=assignment_id, user=user)
            assignment.delete()
            
            logger.info(f"Deleted assignment via API: {assignment_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "作業刪除成功"
            }, status=status.HTTP_200_OK)
            
        except AssignmentV2.DoesNotExist:
            return Response({
                "error": "assignment_not_found",
                "message": "找不到指定的作業",
                "code": "ASSIGNMENT_NOT_FOUND"
            }, status=status.HTTP_404_NOT_FOUND)
    
    except PermissionDeniedError as e:
        logger.warning(f"Permission denied deleting assignment: {str(e)}")
        return Response({
            "error": "permission_denied",
            "message": str(e),
            "code": "CLASSROOM_DATA_READONLY" if "Google Classroom" in str(e) else "PERMISSION_DENIED"
        }, status=status.HTTP_403_FORBIDDEN)
    
    except WebDataError as e:
        logger.error(f"WebData error deleting assignment: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error deleting assignment: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "刪除作業時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_assignments(request):
    """
    查詢作業列表
    
    GET /api/web/assignments/list/?line_user_id=U123456789&status=pending&upcomingWithinDays=7
    """
    try:
        # 驗證必要參數
        line_user_id = request.GET.get('line_user_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 準備篩選條件
        filters = {}
        if request.GET.get('status'):
            filters['status'] = request.GET.get('status')
        
        if request.GET.get('upcomingWithinDays'):
            try:
                filters['upcomingWithinDays'] = int(request.GET.get('upcomingWithinDays'))
            except ValueError:
                return Response({
                    "error": "invalid_parameter",
                    "message": "upcomingWithinDays 必須是數字",
                    "code": "INVALID_DAYS_PARAMETER"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 獲取作業列表
        assignments = WebDataService.get_integrated_assignments(user, **filters)
        
        logger.info(f"Retrieved {len(assignments)} assignments via API for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": {
                "assignments": assignments,
                "total": len(assignments),
                "filters": filters
            }
        }, status=status.HTTP_200_OK)
    
    except WebDataError as e:
        logger.error(f"WebData error listing assignments: {str(e)}")
        return Response({
            "error": "data_error",
            "message": str(e),
            "code": "WEB_DATA_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error listing assignments: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取作業列表時發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)