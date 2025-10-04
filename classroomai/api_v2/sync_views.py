"""
同步相關的 API 視圖
處理 Google Classroom 與本地資料的同步
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from user.models import LineProfile
from services.classroom_sync_service import ClassroomSyncService, ClassroomSyncError
from services.auto_sync_trigger import AutoSyncTrigger, SyncNotificationService
from services.error_handler import handle_api_errors, rate_limit
from services.calendar_sync_service import CalendarSyncService

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
@rate_limit(limit=10, window=300)  # 每5分鐘最多10次全量同步
def sync_classroom_to_v2(request):
    """
    全量同步 Google Classroom 課程和作業到 V2
    
    POST /api/sync/classroom-to-v2/
    {
        "line_user_id": "U123456789"
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        logger.info(f"Starting full classroom sync for user: {line_user_id}")
        
        # 執行同步
        sync_service = ClassroomSyncService(line_user_id)
        sync_result = sync_service.sync_all_courses()
        
        if sync_result['success']:
            logger.info(f"Full sync completed successfully for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "同步完成",
                "data": {
                    "courses_synced": sync_result['courses_synced'],
                    "assignments_synced": sync_result['assignments_synced'],
                    "user_id": line_user_id
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Full sync completed with errors for user: {line_user_id}")
            return Response({
                "success": False,
                "message": "同步完成但有部分錯誤",
                "data": {
                    "courses_synced": sync_result['courses_synced'],
                    "assignments_synced": sync_result['assignments_synced'],
                    "errors": sync_result['errors']
                }
            }, status=status.HTTP_207_MULTI_STATUS)
    
    except ClassroomSyncError as e:
        logger.error(f"Classroom sync error for user {line_user_id}: {str(e)}")
        return Response({
            "error": "sync_error",
            "message": str(e),
            "code": "CLASSROOM_SYNC_FAILED"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error during full sync for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "同步過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
@rate_limit(limit=5, window=300)  # 每5分鐘最多5次統一同步
def manual_sync_all(request):
    """
    手動同步所有 Google 服務（Classroom + Calendar）
    
    POST /api/v2/sync/manual-sync-all/
    {
        "line_user_id": "U123456789"
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        logger.info(f"Starting manual sync all for user: {line_user_id}")
        
        sync_results = {
            "classroom": {"success": False, "error": None},
            "calendar": {"success": False, "error": None}
        }
        
        # 1. 同步 Google Classroom
        try:
            classroom_service = ClassroomSyncService(line_user_id)
            classroom_result = classroom_service.sync_all_courses()
            sync_results["classroom"] = {
                "success": classroom_result['success'],
                "courses_synced": classroom_result.get('courses_synced', 0),
                "assignments_synced": classroom_result.get('assignments_synced', 0),
                "errors": classroom_result.get('errors', [])
            }
            logger.info(f"Classroom sync completed for user: {line_user_id}")
        except Exception as e:
            sync_results["classroom"]["error"] = str(e)
            logger.error(f"Classroom sync failed for user {line_user_id}: {str(e)}")
        
        # 2. 同步 Google Calendar
        try:
            calendar_service = CalendarSyncService(line_user_id)
            calendar_result = calendar_service.sync_events_for_user(line_user_id)
            sync_results["calendar"] = {
                "success": calendar_result.get('success', False),
                "events_synced": calendar_result.get('events_synced', 0),
                "errors": calendar_result.get('errors', [])
            }
            logger.info(f"Calendar sync completed for user: {line_user_id}")
        except Exception as e:
            sync_results["calendar"]["error"] = str(e)
            logger.error(f"Calendar sync failed for user {line_user_id}: {str(e)}")
        
        # 計算整體成功狀態
        overall_success = sync_results["classroom"]["success"] and sync_results["calendar"]["success"]
        
        # 發送同步通知
        try:
            SyncNotificationService.send_sync_notification(line_user_id, sync_results, 'manual_sync_all')
        except Exception as e:
            logger.warning(f"Failed to send sync notification: {str(e)}")
        
        return Response({
            "success": overall_success,
            "message": "手動同步完成" if overall_success else "同步完成但有部分錯誤",
            "data": {
                "sync_results": sync_results,
                "user_id": line_user_id,
                "sync_time": timezone.now().isoformat(),
                "sync_type": "manual_all"
            }
        }, status=status.HTTP_200_OK if overall_success else status.HTTP_207_MULTI_STATUS)
    
    except Exception as e:
        logger.error(f"Unexpected error during manual sync all for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "手動同步過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
@rate_limit(limit=30, window=300)  # 每5分鐘最多30次單一課程同步
def sync_classroom_course(request):
    """
    同步單一 Google Classroom 課程的作業
    
    POST /api/sync/classroom-course/
    {
        "line_user_id": "U123456789",
        "google_course_id": "123456789"
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        google_course_id = request.data.get('google_course_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not google_course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 google_course_id 參數",
                "code": "MISSING_GOOGLE_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        logger.info(f"Starting single course sync for user: {line_user_id}, course: {google_course_id}")
        
        # 執行同步
        sync_service = ClassroomSyncService(line_user_id)
        sync_result = sync_service.sync_single_course(google_course_id)
        
        if sync_result['success']:
            logger.info(f"Single course sync completed successfully: {google_course_id}")
            
            # 發送同步成功通知
            SyncNotificationService.send_sync_notification(line_user_id, sync_result, 'manual_sync')
            
            return Response({
                "success": True,
                "message": "課程同步完成",
                "data": {
                    "course_id": google_course_id,
                    "assignments_synced": sync_result['assignments_synced'],
                    "user_id": line_user_id,
                    "sync_type": "manual"
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Single course sync failed: {google_course_id}")
            
            # 發送同步失敗通知
            SyncNotificationService.send_sync_notification(line_user_id, sync_result, 'manual_sync')
            
            return Response({
                "success": False,
                "message": "課程同步失敗",
                "data": {
                    "course_id": google_course_id,
                    "errors": sync_result['errors']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except ClassroomSyncError as e:
        logger.error(f"Classroom sync error for course {google_course_id}: {str(e)}")
        return Response({
            "error": "sync_error",
            "message": str(e),
            "code": "CLASSROOM_SYNC_FAILED"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error during course sync {google_course_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "同步過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def trigger_auto_sync(request):
    """
    觸發自動同步（用於 Classroom 操作後的自動同步）
    
    POST /api/sync/auto-trigger/
    {
        "line_user_id": "U123456789",
        "google_course_id": "123456789",
        "operation": "create|update|delete",
        "coursework_id": "456789" (可選，作業相關操作時使用)
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        google_course_id = request.data.get('google_course_id')
        operation = request.data.get('operation', 'update')
        coursework_id = request.data.get('coursework_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not google_course_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 google_course_id 參數",
                "code": "MISSING_GOOGLE_COURSE_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        logger.info(f"Auto sync trigger requested for user: {line_user_id}, course: {google_course_id}, operation: {operation}")
        
        # 根據是否有 coursework_id 決定觸發類型
        if coursework_id:
            # 作業相關操作
            sync_result = AutoSyncTrigger.trigger_assignment_sync(
                line_user_id, google_course_id, coursework_id, operation
            )
        else:
            # 課程相關操作
            sync_result = AutoSyncTrigger.trigger_course_sync(
                line_user_id, google_course_id, operation
            )
        
        if sync_result['success']:
            logger.info(f"Auto sync completed successfully for course: {google_course_id}")
            
            # 發送通知
            SyncNotificationService.send_sync_notification(line_user_id, sync_result, f'auto_{operation}')
            
            return Response({
                "success": True,
                "message": "自動同步完成",
                "data": {
                    "course_id": google_course_id,
                    "assignments_synced": sync_result['assignments_synced'],
                    "operation": operation,
                    "sync_type": "auto",
                    "coursework_id": coursework_id
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Auto sync failed for course: {google_course_id}")
            
            # 發送失敗通知
            SyncNotificationService.send_sync_notification(line_user_id, sync_result, f'auto_{operation}')
            
            return Response({
                "success": False,
                "message": "自動同步失敗",
                "data": {
                    "course_id": google_course_id,
                    "operation": operation,
                    "errors": sync_result.get('errors', [])
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected error during auto sync trigger: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "自動同步觸發過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_sync_status(request):
    """
    獲取同步狀態
    
    GET /api/sync/status/?line_user_id=U123456789&google_course_id=123456789
    """
    try:
        # 驗證請求參數
        line_user_id = request.GET.get('line_user_id')
        google_course_id = request.GET.get('google_course_id')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 獲取同步狀態
        status_result = AutoSyncTrigger.get_sync_status(line_user_id, google_course_id)
        
        if status_result['success']:
            return Response({
                "success": True,
                "data": status_result['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": status_result['message'],
                "code": "SYNC_STATUS_ERROR"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取同步狀態時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(["GET"])
@permission_classes([AllowAny])
@handle_api_errors
def check_google_api_status(request):
    """
    檢查 Google API 狀態和權限
    
    GET /api/v2/sync/google-status/?line_user_id=U123456789
    """
    # 驗證請求參數
    line_user_id = request.GET.get('line_user_id')
    
    if not line_user_id:
        return Response({
            "error": "missing_parameter",
            "message": "缺少 line_user_id 參數",
            "code": "MISSING_LINE_USER_ID"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 驗證使用者存在
    user = get_object_or_404(LineProfile, line_user_id=line_user_id)
    
    try:
        # 初始化同步服務
        sync_service = ClassroomSyncService(line_user_id)
        
        # 檢查 API 配額狀態
        quota_status = sync_service.get_api_quota_status()
        
        # 驗證權限
        permission_status = sync_service.validate_permissions()
        
        return Response({
            "success": True,
            "data": {
                "quota_status": quota_status,
                "permission_status": permission_status,
                "user_id": line_user_id,
                "check_time": timezone.now().isoformat()
            }
        }, status=status.HTTP_200_OK)
    
    except ClassroomSyncError as e:
        return Response({
            "success": False,
            "error": "sync_service_error",
            "message": str(e),
            "code": "SYNC_SERVICE_INIT_FAILED"
        }, status=status.HTTP_400_BAD_REQUEST)