"""
API V2 Calendar Views
提供 Google Calendar 相關的 API 端點
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from user.models import LineProfile
from services.error_handler import handle_api_errors, rate_limit

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
@handle_api_errors
def get_calendar_events(request):
    """
    獲取 Google Calendar 事件
    
    GET /api/v2/calendar/get_calendar_events/?line_user_id=U123456789&calendar_id=primary&time_min=...&time_max=...&max_results=10
    """
    try:
        # 驗證請求參數
        line_user_id = request.GET.get('line_user_id')
        calendar_id = request.GET.get('calendar_id', 'primary')
        time_min = request.GET.get('time_min')
        time_max = request.GET.get('time_max')
        max_results = int(request.GET.get('max_results', 10))
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查用戶是否有 Google 憑證
        if not user.google_access_token:
            return Response({
                "success": False,
                "message": "Google Calendar 尚未授權",
                "code": "NOT_AUTHORIZED",
                "data": []
            }, status=status.HTTP_200_OK)
        
        # 嘗試導入 Calendar 同步服務
        try:
            from services.calendar_sync_service import CalendarSyncService
        except ImportError:
            # 如果沒有 CalendarSyncService，返回空數據
            logger.warning("CalendarSyncService not available, returning empty calendar events")
            return Response({
                "success": True,
                "message": "Calendar 服務暫時不可用",
                "data": []
            }, status=status.HTTP_200_OK)
        
        logger.info(f"Getting calendar events for user: {line_user_id}")
        
        # 初始化 Calendar 同步服務
        calendar_service = CalendarSyncService(line_user_id)
        
        # 構建查詢參數
        query_params = {
            'calendar_id': calendar_id,
            'max_results': max_results
        }
        
        if time_min:
            query_params['time_min'] = time_min
        if time_max:
            query_params['time_max'] = time_max
        
        # 獲取事件
        events_result = calendar_service.get_events(**query_params)
        
        if events_result.get('success', True):
            events = events_result.get('events', [])
            
            # 格式化事件數據
            formatted_events = []
            for event in events:
                formatted_event = {
                    'id': event.get('id', ''),
                    'summary': event.get('summary', ''),
                    'description': event.get('description', ''),
                    'start': event.get('start', {}),
                    'end': event.get('end', {}),
                    'location': event.get('location', ''),
                    'status': event.get('status', 'confirmed'),
                    'created': event.get('created', ''),
                    'updated': event.get('updated', ''),
                    'htmlLink': event.get('htmlLink', ''),
                    'attendees': event.get('attendees', [])
                }
                formatted_events.append(formatted_event)
            
            logger.info(f"Successfully retrieved {len(formatted_events)} calendar events for user: {line_user_id}")
            return Response({
                "success": True,
                "data": formatted_events,
                "total_count": len(formatted_events),
                "calendar_id": calendar_id,
                "user_id": line_user_id
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to get calendar events for user: {line_user_id}")
            return Response({
                "success": False,
                "message": events_result.get('message', 'Failed to get calendar events'),
                "data": [],
                "code": "CALENDAR_FETCH_FAILED"
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting calendar events for user {line_user_id}: {str(e)}")
        return Response({
            "success": False,
            "message": "獲取 Calendar 事件時發生錯誤",
            "data": [],
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
def create_calendar_event(request):
    """
    創建 Google Calendar 事件
    
    POST /api/v2/calendar/create_calendar_event/
    {
        "line_user_id": "U123456789",
        "calendar_id": "primary",
        "summary": "事件標題",
        "description": "事件描述",
        "start_datetime": "2024-01-01T10:00:00Z",
        "end_datetime": "2024-01-01T11:00:00Z",
        "location": "地點",
        "attendees": ["email1@example.com", "email2@example.com"]
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        calendar_id = request.data.get('calendar_id', 'primary')
        summary = request.data.get('summary')
        description = request.data.get('description', '')
        start_datetime = request.data.get('start_datetime')
        end_datetime = request.data.get('end_datetime')
        location = request.data.get('location', '')
        attendees = request.data.get('attendees', [])
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not summary or not start_datetime or not end_datetime:
            return Response({
                "error": "missing_parameter",
                "message": "缺少必要參數：summary, start_datetime, end_datetime",
                "code": "MISSING_REQUIRED_FIELDS"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查用戶是否有 Google 憑證
        if not user.google_access_token:
            return Response({
                "success": False,
                "message": "Google Calendar 尚未授權",
                "code": "NOT_AUTHORIZED"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 嘗試導入 Calendar 同步服務
        try:
            from services.calendar_sync_service import CalendarSyncService
        except ImportError:
            return Response({
                "success": False,
                "message": "Calendar 服務暫時不可用",
                "code": "SERVICE_UNAVAILABLE"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        logger.info(f"Creating calendar event for user: {line_user_id}")
        
        # 初始化 Calendar 同步服務
        calendar_service = CalendarSyncService(line_user_id)
        
        # 創建事件
        event_data = {
            'calendar_id': calendar_id,
            'summary': summary,
            'description': description,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'location': location,
            'attendees': attendees
        }
        
        create_result = calendar_service.create_event(**event_data)
        
        if create_result.get('success', True):
            logger.info(f"Successfully created calendar event for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "事件創建成功",
                "data": create_result.get('event', {}),
                "user_id": line_user_id
            }, status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"Failed to create calendar event for user: {line_user_id}")
            return Response({
                "success": False,
                "message": create_result.get('message', 'Failed to create calendar event'),
                "code": "CALENDAR_CREATE_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error creating calendar event for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "創建 Calendar 事件時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([AllowAny])
@handle_api_errors
def update_calendar_event(request):
    """
    更新 Google Calendar 事件
    
    PATCH /api/v2/calendar/update_calendar_event/
    {
        "line_user_id": "U123456789",
        "calendar_id": "primary",
        "event_id": "event_id_here",
        "summary": "更新的標題",
        "description": "更新的描述",
        "start_datetime": "2024-01-01T10:00:00Z",
        "end_datetime": "2024-01-01T11:00:00Z",
        "location": "新地點",
        "attendees": ["email1@example.com"]
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        calendar_id = request.data.get('calendar_id', 'primary')
        event_id = request.data.get('event_id')
        
        if not line_user_id or not event_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少必要參數：line_user_id, event_id",
                "code": "MISSING_REQUIRED_FIELDS"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查用戶是否有 Google 憑證
        if not user.google_access_token:
            return Response({
                "success": False,
                "message": "Google Calendar 尚未授權",
                "code": "NOT_AUTHORIZED"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 嘗試導入 Calendar 同步服務
        try:
            from services.calendar_sync_service import CalendarSyncService
        except ImportError:
            return Response({
                "success": False,
                "message": "Calendar 服務暫時不可用",
                "code": "SERVICE_UNAVAILABLE"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        logger.info(f"Updating calendar event {event_id} for user: {line_user_id}")
        
        # 初始化 Calendar 同步服務
        calendar_service = CalendarSyncService(line_user_id)
        
        # 構建更新數據
        update_data = {
            'calendar_id': calendar_id,
            'event_id': event_id
        }
        
        # 添加可選更新字段
        optional_fields = ['summary', 'description', 'start_datetime', 'end_datetime', 'location', 'attendees']
        for field in optional_fields:
            if field in request.data:
                update_data[field] = request.data[field]
        
        # 更新事件
        update_result = calendar_service.update_event(**update_data)
        
        if update_result.get('success', True):
            logger.info(f"Successfully updated calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "事件更新成功",
                "data": update_result.get('event', {}),
                "user_id": line_user_id
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to update calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": False,
                "message": update_result.get('message', 'Failed to update calendar event'),
                "code": "CALENDAR_UPDATE_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error updating calendar event {event_id} for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "更新 Calendar 事件時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([AllowAny])
@handle_api_errors
def delete_calendar_event(request):
    """
    刪除 Google Calendar 事件
    
    DELETE /api/v2/calendar/delete_calendar_event/
    {
        "line_user_id": "U123456789",
        "calendar_id": "primary",
        "event_id": "event_id_here"
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        calendar_id = request.data.get('calendar_id', 'primary')
        event_id = request.data.get('event_id')
        
        if not line_user_id or not event_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少必要參數：line_user_id, event_id",
                "code": "MISSING_REQUIRED_FIELDS"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查用戶是否有 Google 憑證
        if not user.google_access_token:
            return Response({
                "success": False,
                "message": "Google Calendar 尚未授權",
                "code": "NOT_AUTHORIZED"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 嘗試導入 Calendar 同步服務
        try:
            from services.calendar_sync_service import CalendarSyncService
        except ImportError:
            return Response({
                "success": False,
                "message": "Calendar 服務暫時不可用",
                "code": "SERVICE_UNAVAILABLE"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        logger.info(f"Deleting calendar event {event_id} for user: {line_user_id}")
        
        # 初始化 Calendar 同步服務
        calendar_service = CalendarSyncService(line_user_id)
        
        # 刪除事件
        delete_result = calendar_service.delete_event(
            calendar_id=calendar_id,
            event_id=event_id
        )
        
        if delete_result.get('success', True):
            logger.info(f"Successfully deleted calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "事件刪除成功",
                "user_id": line_user_id
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to delete calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": False,
                "message": delete_result.get('message', 'Failed to delete calendar event'),
                "code": "CALENDAR_DELETE_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error deleting calendar event {event_id} for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "刪除 Calendar 事件時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@handle_api_errors
def manage_calendar_attendees(request):
    """
    管理 Google Calendar 事件參與者
    
    POST /api/v2/calendar/events/attendees/
    {
        "line_user_id": "U123456789",
        "calendar_id": "primary",
        "event_id": "event_id_here",
        "attendees": ["email1@example.com", "email2@example.com"],
        "attendees_to_remove": ["email3@example.com"]
    }
    """
    try:
        # 驗證請求參數
        line_user_id = request.data.get('line_user_id')
        calendar_id = request.data.get('calendar_id', 'primary')
        event_id = request.data.get('event_id')
        attendees = request.data.get('attendees', [])
        attendees_to_remove = request.data.get('attendees_to_remove', [])
        
        if not line_user_id or not event_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少必要參數：line_user_id, event_id",
                "code": "MISSING_REQUIRED_FIELDS"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查用戶是否有 Google 憑證
        if not user.google_access_token:
            return Response({
                "success": False,
                "message": "Google Calendar 尚未授權",
                "code": "NOT_AUTHORIZED"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 嘗試導入 Calendar 同步服務
        try:
            from services.calendar_sync_service import CalendarSyncService
        except ImportError:
            return Response({
                "success": False,
                "message": "Calendar 服務暫時不可用",
                "code": "SERVICE_UNAVAILABLE"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        logger.info(f"Managing attendees for calendar event {event_id} for user: {line_user_id}")
        
        # 初始化 Calendar 同步服務
        calendar_service = CalendarSyncService(line_user_id)
        
        # 管理參與者
        manage_result = calendar_service.manage_attendees(
            calendar_id=calendar_id,
            event_id=event_id,
            attendees=attendees,
            attendees_to_remove=attendees_to_remove
        )
        
        if manage_result.get('success', True):
            logger.info(f"Successfully managed attendees for calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": True,
                "message": "參與者管理成功",
                "data": manage_result.get('event', {}),
                "user_id": line_user_id
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to manage attendees for calendar event {event_id} for user: {line_user_id}")
            return Response({
                "success": False,
                "message": manage_result.get('message', 'Failed to manage calendar attendees'),
                "code": "CALENDAR_ATTENDEES_FAILED"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error managing attendees for calendar event {event_id} for user {line_user_id}: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "管理 Calendar 參與者時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)