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

from services.preview_sync_service import PreviewSyncService

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
        
        logger.info(f"Starting classroom sync to V2 for user: {line_user_id}")
        
        # 執行同步
        classroom_service = ClassroomSyncService(line_user_id)
        sync_result = classroom_service.sync_all_courses()
        
        if sync_result['success']:
            logger.info(f"Classroom sync to V2 completed for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "Google Classroom 同步完成",
                "data": sync_result
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Classroom sync to V2 failed for user: {line_user_id}")
            return Response({
                "success": False,
                "message": "Google Classroom 同步失敗",
                "data": sync_result
            }, status=status.HTTP_207_MULTI_STATUS)
    
    except ClassroomSyncError as e:
        logger.error(f"Classroom sync service error for user {line_user_id}: {str(e)}")
        return Response({
            "error": "sync_service_error",
            "message": str(e),
            "code": "CLASSROOM_SYNC_SERVICE_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Unexpected error during classroom sync for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "同步過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
@rate_limit(limit=5, window=300)  # 每5分鐘最多5次預覽同步
def preview_sync_all(request):
    """
    預覽所有 Google 服務的同步資料（不寫入資料庫）
    
    POST /api/v2/sync/preview-sync-all/
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
        
        logger.info(f"Starting preview sync for user: {line_user_id}")
        
        # 執行預覽同步
        preview_service = PreviewSyncService(line_user_id)
        preview_result = preview_service.preview_all_sync_data()
        
        if preview_result['success']:
            logger.info(f"Preview sync completed for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "預覽同步完成",
                "data": {
                    "preview_data": preview_result,
                    "user_id": line_user_id,
                    "preview_time": timezone.now().isoformat()
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Preview sync failed for user: {line_user_id}")
            return Response({
                "success": False,
                "message": "預覽同步失敗",
                "data": {
                    "errors": preview_result.get('errors', []),
                    "user_id": line_user_id
                }
            }, status=status.HTTP_207_MULTI_STATUS)
    
    except ClassroomSyncError as e:
        logger.error(f"Preview sync service error for user {line_user_id}: {str(e)}")
        return Response({
            "error": "sync_service_error",
            "message": str(e),
            "code": "PREVIEW_SYNC_SERVICE_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Unexpected error during preview sync for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "預覽同步過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
@rate_limit(limit=5, window=300)  # 每5分鐘最多5次確認匯入
def confirm_import(request):
    """
    確認匯入選擇的 Google Classroom 項目到資料庫
    
    POST /api/v2/sync/confirm-import/
    {
        "line_user_id": "U123456789",
        "selected_items": {
            "courses": ["course_id_1", "course_id_2"],
            "assignments": ["assignment_id_1", "assignment_id_2"]
        }
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        selected_items = request.data.get('selected_items', {})
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not selected_items:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 selected_items 參數",
                "code": "MISSING_SELECTED_ITEMS"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        logger.info(f"Starting confirm import for user: {line_user_id}")
        
        import_results = {
            "classroom": {"success": False, "error": None}
        }
        
        # 1. 匯入選擇的 Google Classroom 項目
        selected_courses = selected_items.get('courses', [])
        selected_assignments = selected_items.get('assignments', [])
        
        if selected_courses or selected_assignments:
            try:
                classroom_service = ClassroomSyncService(line_user_id)
                
                # 如果有選擇課程，進行選擇性同步
                if selected_courses:
                    classroom_result = classroom_service._selective_sync_courses(selected_courses)
                    import_results["classroom"] = {
                        "success": classroom_result.get('success', False),
                        "courses_imported": len(selected_courses),
                        "assignments_imported": classroom_result.get('assignments_synced', 0),
                        "errors": classroom_result.get('errors', [])
                    }
                else:
                    import_results["classroom"] = {
                        "success": True,
                        "courses_imported": 0,
                        "assignments_imported": 0,
                        "errors": []
                    }
                
                logger.info(f"Classroom import completed for user: {line_user_id}")
            except Exception as e:
                import_results["classroom"]["error"] = str(e)
                logger.error(f"Classroom import failed for user {line_user_id}: {str(e)}")
        
        # 計算整體成功狀態
        overall_success = (
            (not selected_courses and not selected_assignments) or import_results["classroom"]["success"]
        )
        
        # 發送匯入通知
        try:
            SyncNotificationService.send_sync_notification(line_user_id, import_results, 'selective_import')
        except Exception as e:
            logger.warning(f"Failed to send import notification: {str(e)}")
        
        return Response({
            "success": overall_success,
            "message": "選擇性匯入完成" if overall_success else "匯入完成但有部分錯誤",
            "data": {
                "import_results": import_results,
                "selected_items": selected_items,
                "user_id": line_user_id,
                "import_time": timezone.now().isoformat(),
                "import_type": "selective"
            }
        }, status=status.HTTP_200_OK if overall_success else status.HTTP_207_MULTI_STATUS)
    
    except Exception as e:
        logger.error(f"Unexpected error during confirm import for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "確認匯入過程中發生未預期錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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