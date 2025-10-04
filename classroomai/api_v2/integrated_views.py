"""
整合查詢 API 視圖
提供 Classroom 和本地資料的整合查詢功能
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from user.models import LineProfile
from services.integrated_query_service import IntegratedQueryService
from services.n8n_workflow_service import N8nWorkflowService
from django.utils import timezone

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_integrated_courses(request):
    """
    獲取整合的課程列表（V2 本地 + Classroom 即時）
    
    GET /api/v2/integrated/courses/?line_user_id=U123456789&include_classroom=true
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
        
        # 解析參數
        include_classroom = request.GET.get('include_classroom', 'true').lower() == 'true'
        
        # 獲取整合課程列表
        query_service = IntegratedQueryService(line_user_id)
        courses = query_service.get_integrated_courses(include_classroom=include_classroom)
        
        logger.info(f"Retrieved {len(courses)} integrated courses for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": {
                "courses": courses,
                "total": len(courses),
                "include_classroom": include_classroom
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving integrated courses: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取課程列表時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_integrated_assignments(request):
    """
    獲取整合的作業列表（V2 本地 + Classroom 即時）
    
    GET /api/v2/integrated/assignments/?line_user_id=U123456789&status=pending&upcomingWithinDays=7
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
        
        # 獲取整合作業列表
        query_service = IntegratedQueryService(line_user_id)
        assignments = query_service.get_integrated_assignments(**filters)
        
        logger.info(f"Retrieved {len(assignments)} integrated assignments for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": {
                "assignments": assignments,
                "total": len(assignments),
                "filters": filters
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving integrated assignments: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取作業列表時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_course_summary(request):
    """
    獲取課程摘要統計
    
    GET /api/v2/integrated/summary/?line_user_id=U123456789
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
        
        # 獲取課程摘要
        query_service = IntegratedQueryService(line_user_id)
        summary = query_service.get_course_summary()
        
        logger.info(f"Retrieved course summary for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": summary
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving course summary: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取課程摘要時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_courses_and_assignments(request):
    """
    搜尋課程和作業
    
    GET /api/v2/integrated/search/?line_user_id=U123456789&q=資料結構
    """
    try:
        # 驗證必要參數
        line_user_id = request.GET.get('line_user_id')
        query = request.GET.get('q')
        
        if not line_user_id:
            return Response({
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not query:
            return Response({
                "error": "missing_parameter",
                "message": "缺少搜尋關鍵字 q 參數",
                "code": "MISSING_QUERY"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 執行搜尋
        query_service = IntegratedQueryService(line_user_id)
        search_results = query_service.search_courses_and_assignments(query)
        
        logger.info(f"Search completed for user: {line_user_id}, query: {query}, results: {search_results['total_results']}")
        
        return Response({
            "success": True,
            "data": search_results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error searching courses and assignments: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "搜尋時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_dashboard_data(request):
    """
    獲取儀表板資料（整合摘要 + 即將到期作業）
    
    GET /api/v2/integrated/dashboard/?line_user_id=U123456789
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
        
        # 獲取整合資料
        query_service = IntegratedQueryService(line_user_id)
        
        # 獲取摘要統計
        summary = query_service.get_course_summary()
        
        # 獲取即將到期的作業（7天內）
        upcoming_assignments = query_service.get_integrated_assignments(
            status='pending',
            upcomingWithinDays=7
        )
        
        # 獲取最近的課程（最多5個）
        recent_courses = query_service.get_integrated_courses(include_classroom=False)[:5]
        
        dashboard_data = {
            'summary': summary,
            'upcoming_assignments': upcoming_assignments[:10],  # 最多10個即將到期作業
            'recent_courses': recent_courses,
            'last_updated': timezone.now().isoformat()
        }
        
        logger.info(f"Retrieved dashboard data for user: {line_user_id}")
        
        return Response({
            "success": True,
            "data": dashboard_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取儀表板資料時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def process_n8n_intent(request):
    """
    處理 n8n 工作流意圖
    
    POST /api/v2/integrated/n8n-intent/
    {
        "line_user_id": "U123456789",
        "intent": "create_local_course",
        "parameters": {
            "title": "機器學習導論",
            "instructor": "張教授"
        }
    }
    """
    try:
        # 驗證請求資料
        if not request.data:
            return Response({
                "success": False,
                "error": "missing_data",
                "message": "缺少請求資料",
                "code": "MISSING_REQUEST_DATA"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        line_user_id = request.data.get('line_user_id')
        if not line_user_id:
            return Response({
                "success": False,
                "error": "missing_parameter",
                "message": "缺少 line_user_id 參數",
                "code": "MISSING_LINE_USER_ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證使用者存在
        user = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 準備意圖資料
        intent_data = {
            'intent': request.data.get('intent'),
            'parameters': request.data.get('parameters', {}),
            'confidence': request.data.get('confidence', 1.0)
        }
        
        if not intent_data['intent']:
            return Response({
                "success": False,
                "error": "missing_parameter",
                "message": "缺少 intent 參數",
                "code": "MISSING_INTENT"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 處理意圖
        result = N8nWorkflowService.process_intent(intent_data, line_user_id)
        
        # 根據結果回傳適當的 HTTP 狀態碼
        if result['success']:
            logger.info(f"N8n intent processed successfully: {intent_data['intent']} for user: {line_user_id}")
            return Response(result, status=status.HTTP_200_OK)
        else:
            # 根據錯誤類型決定狀態碼
            error_code = result.get('code', '')
            if error_code in ['MISSING_PARAMETER', 'INVALID_INTENT', 'MISSING_SCHEDULE']:
                http_status = status.HTTP_400_BAD_REQUEST
            elif error_code in ['USER_NOT_FOUND', 'COURSE_NOT_FOUND', 'ASSIGNMENT_NOT_FOUND']:
                http_status = status.HTTP_404_NOT_FOUND
            elif error_code in ['CLASSROOM_DATA_READONLY']:
                http_status = status.HTTP_403_FORBIDDEN
            else:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            logger.warning(f"N8n intent processing failed: {result['message']} for user: {line_user_id}")
            return Response(result, status=http_status)
    
    except Exception as e:
        logger.error(f"Error processing n8n intent: {str(e)}")
        return Response({
            "success": False,
            "error": "internal_error",
            "message": "處理意圖時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)