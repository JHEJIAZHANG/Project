"""
Legacy API 視圖
提供與前端相容的 API 端點，支援整合資料
"""
import logging
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from user.models import LineProfile
from services.integrated_query_service import IntegratedQueryService
from services.web_data_service import WebDataService
from api_v2.models import CustomCategory, CustomTodoItem, CourseV2, NoteV2
from api_v2.validators import APIValidator

logger = logging.getLogger(__name__)


@api_view(["GET", "HEAD"])
@permission_classes([AllowAny])
def get_courses(request):
    """
    獲取課程列表（整合本地和鏡像資料）
    
    GET /api/v2/courses/?line_user_id=U123456789&page=1&page_size=10&source=local&search=資料結構
    HEAD /api/v2/courses/?line_user_id=U123456789
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
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
        # 獲取整合課程列表
        query_service = IntegratedQueryService(line_user_id)
        courses = query_service.get_integrated_courses(include_classroom=True)
        
        # 轉換為前端期望的格式
        formatted_courses = []
        for course in courses:
            formatted_course = {
                'id': course['id'],
                'title': course['title'],
                'description': course['description'],
                'instructor': course['instructor'],
                'classroom': course['classroom'],
                'color': course['color'],
                'source': course['source'],  # local, classroom_mirror, classroom_live
                'is_google_classroom': course['is_google_classroom'],
                'google_classroom_id': course.get('google_classroom_id'),
                'created_at': course['created_at'],
                'updated_at': course['updated_at'],
                'schedules': course['schedules']
            }
            formatted_courses.append(formatted_course)
        
        logger.info(f"Retrieved {len(formatted_courses)} courses for user: {line_user_id}")
        
        return Response(formatted_courses, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving courses: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取課程列表時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "HEAD"])
@permission_classes([AllowAny])
def get_assignments(request):
    """
    獲取作業列表（整合本地和鏡像資料）
    
    GET /api/v2/assignments/?line_user_id=U123456789&status=pending&upcomingWithinDays=7
    HEAD /api/v2/assignments/?line_user_id=U123456789
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
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
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
        
        # 轉換為前端期望的格式
        formatted_assignments = []
        for assignment in assignments:
            formatted_assignment = {
                'id': assignment['id'],
                'title': assignment['title'],
                'description': assignment['description'],
                'due_date': assignment['due_date'],
                'type': assignment['type'],
                'status': assignment['status'],
                'source': assignment['source'],  # local, classroom_mirror, classroom_live
                'is_google_classroom': assignment['is_google_classroom'],
                'google_coursework_id': assignment.get('google_coursework_id'),
                'course': assignment['course'],
                'created_at': assignment['created_at'],
                'updated_at': assignment['updated_at']
            }
            formatted_assignments.append(formatted_assignment)
        
        logger.info(f"Retrieved {len(formatted_assignments)} assignments for user: {line_user_id}")
        
        return Response(formatted_assignments, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving assignments: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取作業列表時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "HEAD", "POST"])
@permission_classes([AllowAny])
def get_custom_categories(request):
    """
    獲取或創建自訂分類
    
    GET /api/v2/custom-categories/?line_user_id=U123456789
    HEAD /api/v2/custom-categories/?line_user_id=U123456789
    POST /api/v2/custom-categories/ (with line_user_id in body)
    """
    if request.method in ["GET", "HEAD"]:
        return _get_custom_categories_list(request)
    elif request.method == "POST":
        return _create_custom_category(request)


def _get_custom_categories_list(request):
    """獲取自訂分類列表"""
    try:
        # 使用新的驗證工具
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='GET', required=True
        )
        if not is_valid:
            return error_response
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
        # 獲取用戶的自訂分類
        from api_v2.models import CustomCategory
        categories = CustomCategory.objects.filter(user=user).order_by('name')
        
        # 轉換為前端期望的格式
        formatted_categories = []
        for category in categories:
            formatted_category = {
                'id': str(category.id),
                'name': category.name,
                'icon': category.icon,
                'color': category.color,
                'createdAt': category.created_at.isoformat(),
                'updatedAt': category.updated_at.isoformat()
            }
            formatted_categories.append(formatted_category)
        
        logger.info(f"Retrieved {len(formatted_categories)} custom categories for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(formatted_categories)
    
    except ImportError as e:
        logger.error(f"Import error in custom categories: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error retrieving custom categories: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "獲取自訂分類時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_custom_category(request):
    """創建新的自訂分類"""
    try:
        import json
        from .models import CustomCategory
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='AUTO', required=True
        )
        if not is_valid:
            return error_response
        
        # 驗證必要欄位
        is_valid, name, error_response = APIValidator.validate_required_field(
            data, 'name', str, min_length=1, max_length=50
        )
        if not is_valid:
            return error_response
        
        # 檢查分類名稱是否已存在
        if CustomCategory.objects.filter(user=user, name=name).exists():
            return APIValidator.create_error_response(
                error_type="duplicate_name",
                message="分類名稱已存在",
                code="DUPLICATE_CATEGORY_NAME",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 處理可選欄位
        icon = data.get('icon', 'clipboard')
        color = data.get('color', '#3b82f6')
        
        # 驗證 icon 和 color 格式
        if icon and len(icon) > 30:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="icon 長度不能超過 30 個字符",
                code="INVALID_ICON_LENGTH",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if color and len(color) > 20:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="color 長度不能超過 20 個字符",
                code="INVALID_COLOR_LENGTH",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 創建分類
        category = CustomCategory.objects.create(
            user=user,
            name=name,
            icon=icon,
            color=color
        )
        
        # 返回創建的分類
        formatted_category = {
            'id': str(category.id),
            'name': category.name,
            'icon': category.icon,
            'color': category.color,
            'createdAt': category.created_at.isoformat(),
            'updatedAt': category.updated_at.isoformat()
        }
        
        logger.info(f"Created custom category {category.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(
            formatted_category, 
            status_code=status.HTTP_201_CREATED
        )
    
    except ImportError as e:
        logger.error(f"Import error in create custom category: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error creating custom category: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "創建自訂分類時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "HEAD", "POST"])
@permission_classes([AllowAny])
def get_custom_todos(request):
    """
    獲取或創建自訂待辦事項
    
    GET /api/v2/custom-todos/?line_user_id=U123456789
    HEAD /api/v2/custom-todos/?line_user_id=U123456789
    POST /api/v2/custom-todos/ (with line_user_id in body)
    """
    if request.method in ["GET", "HEAD"]:
        return _get_custom_todos_list(request)
    elif request.method == "POST":
        return _create_custom_todo(request)


def _get_custom_todos_list(request):
    """獲取自訂待辦事項列表"""
    try:
        # 使用新的驗證工具
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='GET', required=True
        )
        if not is_valid:
            return error_response
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
        # 獲取用戶的自訂待辦事項
        from .models import CustomTodoItem
        todos = CustomTodoItem.objects.filter(user=user).select_related('category', 'course').order_by('-created_at')
        
        # 轉換為前端期望的格式
        formatted_todos = []
        for todo in todos:
            formatted_todo = {
                'id': str(todo.id),
                'title': todo.title,
                'description': todo.description,
                'dueDate': todo.due_date.isoformat(),
                'status': todo.status,
                'category': str(todo.category.id) if todo.category else None,
                'course': str(todo.course.id) if todo.course else None,
                'createdAt': todo.created_at.isoformat(),
                'updatedAt': todo.updated_at.isoformat()
            }
            formatted_todos.append(formatted_todo)
        
        logger.info(f"Retrieved {len(formatted_todos)} custom todos for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(formatted_todos)
    
    except ImportError as e:
        logger.error(f"Import error in custom todos: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error retrieving custom todos: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "獲取自訂待辦事項時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_custom_todo(request):
    """創建新的自訂待辦事項"""
    try:
        import json
        from .models import CustomTodoItem, CustomCategory, CourseV2
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='AUTO', required=True
        )
        if not is_valid:
            return error_response
        
        # 驗證必要欄位
        is_valid, title, error_response = APIValidator.validate_required_field(
            data, 'title', str, min_length=1, max_length=200
        )
        if not is_valid:
            return error_response
        
        # 驗證日期欄位（支援 due_date 和 dueDate 兩種格式）
        due_date_field = 'due_date' if 'due_date' in data else 'dueDate'
        is_valid, due_date, error_response = APIValidator.validate_datetime_field(
            data, due_date_field, required=True
        )
        if not is_valid:
            return error_response
        
        # 處理可選欄位
        description = data.get('description', '')
        if description and len(description) > 1000:  # 限制描述長度
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="description 長度不能超過 1000 個字符",
                code="DESCRIPTION_TOO_LONG",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        status_value = data.get('status', 'pending')
        # 驗證狀態值
        valid_statuses = ['pending', 'completed', 'overdue']
        if status_value not in valid_statuses:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message=f"status 必須是以下值之一: {', '.join(valid_statuses)}",
                code="INVALID_STATUS",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        category_id = data.get('category')
        course_id = data.get('course')
        
        # 驗證分類（如果提供）
        category = None
        if category_id:
            try:
                category = CustomCategory.objects.get(id=category_id, user=user)
            except CustomCategory.DoesNotExist:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="指定的分類不存在",
                    code="INVALID_CATEGORY",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except ValueError:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="無效的分類 ID 格式",
                    code="INVALID_CATEGORY_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # 驗證課程（如果提供）
        course = None
        if course_id:
            try:
                course = CourseV2.objects.get(id=course_id, user=user)
            except CourseV2.DoesNotExist:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="指定的課程不存在",
                    code="INVALID_COURSE",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except ValueError:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="無效的課程 ID 格式",
                    code="INVALID_COURSE_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # 創建待辦事項
        todo = CustomTodoItem.objects.create(
            user=user,
            title=title,
            description=description,
            due_date=due_date,
            status=status_value,
            category=category,
            course=course
        )
        
        # 返回創建的待辦事項
        formatted_todo = {
            'id': str(todo.id),
            'title': todo.title,
            'description': todo.description,
            'dueDate': todo.due_date.isoformat(),
            'status': todo.status,
            'category': str(todo.category.id) if todo.category else None,
            'course': str(todo.course.id) if todo.course else None,
            'createdAt': todo.created_at.isoformat(),
            'updatedAt': todo.updated_at.isoformat()
        }
        
        logger.info(f"Created custom todo {todo.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(
            formatted_todo, 
            status_code=status.HTTP_201_CREATED
        )
    
    except ImportError as e:
        logger.error(f"Import error in create custom todo: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error creating custom todo: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "創建自訂待辦事項時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT", "DELETE"])
@permission_classes([AllowAny])
def manage_custom_category(request, category_id):
    """
    更新或刪除自訂分類
    
    PUT /api/v2/custom-categories/<category_id>/
    DELETE /api/v2/custom-categories/<category_id>/
    """
    if request.method == "PUT":
        return _update_custom_category(request, category_id)
    elif request.method == "DELETE":
        return _delete_custom_category(request, category_id)


def _update_custom_category(request, category_id):
    """更新自訂分類"""
    try:
        import json
        from .models import CustomCategory
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取分類
        try:
            category = CustomCategory.objects.get(id=category_id, user=user)
        except CustomCategory.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="分類不存在",
                code="CATEGORY_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的分類 ID 格式",
                code="INVALID_CATEGORY_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新欄位
        if 'name' in data:
            is_valid, new_name, error_response = APIValidator.validate_required_field(
                data, 'name', str, min_length=1, max_length=50
            )
            if not is_valid:
                return error_response
            
            if new_name != category.name:
                # 檢查新名稱是否已存在
                if CustomCategory.objects.filter(user=user, name=new_name).exists():
                    return APIValidator.create_error_response(
                        error_type="duplicate_name",
                        message="分類名稱已存在",
                        code="DUPLICATE_CATEGORY_NAME",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                category.name = new_name
        
        if 'icon' in data:
            icon = data['icon']
            if icon and len(icon) > 30:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="icon 長度不能超過 30 個字符",
                    code="INVALID_ICON_LENGTH",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            category.icon = icon
        
        if 'color' in data:
            color = data['color']
            if color and len(color) > 20:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="color 長度不能超過 20 個字符",
                    code="INVALID_COLOR_LENGTH",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            category.color = color
        
        # 保存更新
        category.save()
        
        # 返回更新後的分類
        formatted_category = {
            'id': str(category.id),
            'name': category.name,
            'icon': category.icon,
            'color': category.color,
            'createdAt': category.created_at.isoformat(),
            'updatedAt': category.updated_at.isoformat()
        }
        
        logger.info(f"Updated custom category {category.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(formatted_category)
    
    except ImportError as e:
        logger.error(f"Import error in update custom category: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error updating custom category: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "更新自訂分類時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _delete_custom_category(request, category_id):
    """刪除自訂分類"""
    try:
        from .models import CustomCategory
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取並刪除分類
        try:
            category = CustomCategory.objects.get(id=category_id, user=user)
            category_name = category.name  # 保存名稱用於日誌
            category.delete()
            
            logger.info(f"Deleted custom category {category_id} ({category_name}) for user: {user.line_user_id}")
            
            return APIValidator.create_success_response({
                "message": "分類已刪除",
                "id": category_id,
                "name": category_name
            })
            
        except CustomCategory.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="分類不存在",
                code="CATEGORY_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的分類 ID 格式",
                code="INVALID_CATEGORY_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    except ImportError as e:
        logger.error(f"Import error in delete custom category: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error deleting custom category: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "刪除自訂分類時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH", "DELETE"])
@permission_classes([AllowAny])
def manage_custom_todo(request, todo_id):
    """
    更新或刪除自訂待辦事項
    
    PATCH /api/v2/custom-todos/<todo_id>/
    DELETE /api/v2/custom-todos/<todo_id>/
    """
    if request.method == "PATCH":
        return _update_custom_todo(request, todo_id)
    elif request.method == "DELETE":
        return _delete_custom_todo(request, todo_id)


def _update_custom_todo(request, todo_id):
    """更新自訂待辦事項"""
    try:
        import json
        from .models import CustomTodoItem, CustomCategory, CourseV2
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取待辦事項
        try:
            todo = CustomTodoItem.objects.get(id=todo_id, user=user)
        except CustomTodoItem.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="待辦事項不存在",
                code="TODO_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的待辦事項 ID 格式",
                code="INVALID_TODO_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新欄位
        if 'title' in data:
            is_valid, title, error_response = APIValidator.validate_required_field(
                data, 'title', str, min_length=1, max_length=200
            )
            if not is_valid:
                return error_response
            todo.title = title
        
        if 'description' in data:
            description = data['description']
            if description and len(description) > 1000:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="description 長度不能超過 1000 個字符",
                    code="DESCRIPTION_TOO_LONG",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            todo.description = description
        
        if 'due_date' in data or 'dueDate' in data:
            due_date_field = 'due_date' if 'due_date' in data else 'dueDate'
            is_valid, due_date, error_response = APIValidator.validate_datetime_field(
                data, due_date_field, required=True
            )
            if not is_valid:
                return error_response
            todo.due_date = due_date
        
        if 'status' in data:
            status_value = data['status']
            valid_statuses = ['pending', 'completed', 'overdue']
            if status_value not in valid_statuses:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message=f"status 必須是以下值之一: {', '.join(valid_statuses)}",
                    code="INVALID_STATUS",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            todo.status = status_value
        
        if 'category' in data:
            category_id = data['category']
            if category_id:
                try:
                    category = CustomCategory.objects.get(id=category_id, user=user)
                    todo.category = category
                except CustomCategory.DoesNotExist:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="指定的分類不存在",
                        code="INVALID_CATEGORY",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                except ValueError:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="無效的分類 ID 格式",
                        code="INVALID_CATEGORY_ID",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            else:
                todo.category = None
        
        if 'course' in data:
            course_id = data['course']
            if course_id:
                try:
                    course = CourseV2.objects.get(id=course_id, user=user)
                    todo.course = course
                except CourseV2.DoesNotExist:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="指定的課程不存在",
                        code="INVALID_COURSE",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                except ValueError:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="無效的課程 ID 格式",
                        code="INVALID_COURSE_ID",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            else:
                todo.course = None
        
        # 保存更新
        todo.save()
        
        # 返回更新後的待辦事項
        formatted_todo = {
            'id': str(todo.id),
            'title': todo.title,
            'description': todo.description,
            'dueDate': todo.due_date.isoformat(),
            'status': todo.status,
            'category': str(todo.category.id) if todo.category else None,
            'course': str(todo.course.id) if todo.course else None,
            'createdAt': todo.created_at.isoformat(),
            'updatedAt': todo.updated_at.isoformat()
        }
        
        logger.info(f"Updated custom todo {todo.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(formatted_todo)
    
    except ImportError as e:
        logger.error(f"Import error in update custom todo: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error updating custom todo: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "更新自訂待辦事項時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _delete_custom_todo(request, todo_id):
    """刪除自訂待辦事項"""
    try:
        from .models import CustomTodoItem
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取並刪除待辦事項
        try:
            todo = CustomTodoItem.objects.get(id=todo_id, user=user)
            todo_title = todo.title  # 保存標題用於日誌
            todo.delete()
            
            logger.info(f"Deleted custom todo {todo_id} ({todo_title}) for user: {user.line_user_id}")
            
            return APIValidator.create_success_response({
                "message": "待辦事項已刪除",
                "id": todo_id,
                "title": todo_title
            })
            
        except CustomTodoItem.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="待辦事項不存在",
                code="TODO_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的待辦事項 ID 格式",
                code="INVALID_TODO_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    except ImportError as e:
        logger.error(f"Import error in delete custom todo: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error deleting custom todo: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "刪除自訂待辦事項時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "HEAD", "POST"])
@permission_classes([AllowAny])
def get_notes(request):
    """
    獲取或創建筆記
    
    GET /api/v2/notes/?line_user_id=U123456789
    POST /api/v2/notes/ (with line_user_id and note data in body)
    """
    if request.method in ["GET", "HEAD"]:
        return _get_notes_list(request)
    elif request.method == "POST":
        return _create_note(request)


def _get_notes_list(request):
    """獲取筆記列表"""
    try:
        # 使用新的驗證工具
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='GET', required=True
        )
        if not is_valid:
            return error_response
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
        # 獲取用戶的筆記
        from .models import NoteV2
        notes = NoteV2.objects.filter(user=user).select_related('course').order_by('-created_at')
        
        # 獲取篩選參數
        course_id = request.GET.get('course_id')
        search = request.GET.get('search', '').strip()
        
        # 應用篩選
        if course_id:
            try:
                notes = notes.filter(course_id=course_id)
            except ValueError:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="無效的課程 ID 格式",
                    code="INVALID_COURSE_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if search:
            from django.db.models import Q
            notes = notes.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # 分頁處理
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '20')
        
        try:
            page = int(page)
            page_size = int(page_size)
            page_size = min(page_size, 100)  # 限制最大頁面大小
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="page 和 page_size 必須是數字",
                code="INVALID_PAGINATION",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 計算分頁
        total_count = notes.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_notes = notes[start_index:end_index]
        
        # 轉換為前端期望的格式
        formatted_notes = []
        for note in paginated_notes:
            formatted_note = {
                'id': str(note.id),
                'title': note.title,
                'content': note.content,
                'course': {
                    'id': str(note.course.id),
                    'title': note.course.title
                } if note.course else None,
                'createdAt': note.created_at.isoformat(),
                'updatedAt': note.updated_at.isoformat()
            }
            formatted_notes.append(formatted_note)
        
        logger.info(f"Retrieved {len(formatted_notes)} notes for user: {user.line_user_id}")
        
        # 計算分頁元資料
        total_pages = (total_count + page_size - 1) // page_size
        meta = {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
        
        return APIValidator.create_success_response(formatted_notes, meta=meta)
    
    except ImportError as e:
        logger.error(f"Import error in notes: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error retrieving notes: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "獲取筆記時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_note(request):
    """創建新筆記"""
    try:
        import json
        from .models import NoteV2, CourseV2
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='AUTO', required=True
        )
        if not is_valid:
            return error_response
        
        # 驗證必要欄位
        is_valid, title, error_response = APIValidator.validate_required_field(
            data, 'title', str, min_length=1, max_length=255
        )
        if not is_valid:
            return error_response
        
        is_valid, content, error_response = APIValidator.validate_required_field(
            data, 'content', str, min_length=1
        )
        if not is_valid:
            return error_response
        
        # 處理可選的課程關聯
        course = None
        course_id = data.get('course_id')
        if course_id:
            try:
                course = CourseV2.objects.get(id=course_id, user=user)
            except CourseV2.DoesNotExist:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="指定的課程不存在",
                    code="INVALID_COURSE",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except ValueError:
                return APIValidator.create_error_response(
                    error_type="invalid_parameter",
                    message="無效的課程 ID 格式",
                    code="INVALID_COURSE_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # 創建筆記
        note = NoteV2.objects.create(
            user=user,
            title=title,
            content=content,
            course=course
        )
        
        # 返回創建的筆記
        formatted_note = {
            'id': str(note.id),
            'title': note.title,
            'content': note.content,
            'course': {
                'id': str(note.course.id),
                'title': note.course.title
            } if note.course else None,
            'createdAt': note.created_at.isoformat(),
            'updatedAt': note.updated_at.isoformat()
        }
        
        logger.info(f"Created note {note.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(
            formatted_note, 
            status_code=status.HTTP_201_CREATED
        )
    
    except ImportError as e:
        logger.error(f"Import error in create note: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "創建筆記時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def manage_note(request, note_id):
    """
    更新或刪除筆記
    
    PUT/PATCH /api/v2/notes/<note_id>/
    DELETE /api/v2/notes/<note_id>/
    """
    if request.method in ["PUT", "PATCH"]:
        return _update_note(request, note_id)
    elif request.method == "DELETE":
        return _delete_note(request, note_id)


def _update_note(request, note_id):
    """更新筆記"""
    try:
        import json
        from .models import NoteV2, CourseV2
        from .validators import APIValidator
        
        # 解析請求資料
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return APIValidator.create_error_response(
                error_type="invalid_json",
                message="請求資料格式不正確",
                code="INVALID_JSON",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取筆記
        try:
            note = NoteV2.objects.get(id=note_id, user=user)
        except NoteV2.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="筆記不存在",
                code="NOTE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的筆記 ID 格式",
                code="INVALID_NOTE_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新欄位
        if 'title' in data:
            is_valid, title, error_response = APIValidator.validate_required_field(
                data, 'title', str, min_length=1, max_length=255
            )
            if not is_valid:
                return error_response
            note.title = title
        
        if 'content' in data:
            is_valid, content, error_response = APIValidator.validate_required_field(
                data, 'content', str, min_length=1
            )
            if not is_valid:
                return error_response
            note.content = content
        
        if 'course_id' in data:
            course_id = data['course_id']
            if course_id:
                try:
                    course = CourseV2.objects.get(id=course_id, user=user)
                    note.course = course
                except CourseV2.DoesNotExist:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="指定的課程不存在",
                        code="INVALID_COURSE",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                except ValueError:
                    return APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message="無效的課程 ID 格式",
                        code="INVALID_COURSE_ID",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            else:
                note.course = None
        
        # 保存更新
        note.save()
        
        # 返回更新後的筆記
        formatted_note = {
            'id': str(note.id),
            'title': note.title,
            'content': note.content,
            'course': {
                'id': str(note.course.id),
                'title': note.course.title
            } if note.course else None,
            'createdAt': note.created_at.isoformat(),
            'updatedAt': note.updated_at.isoformat()
        }
        
        logger.info(f"Updated note {note.id} for user: {user.line_user_id}")
        
        return APIValidator.create_success_response(formatted_note)
    
    except ImportError as e:
        logger.error(f"Import error in update note: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "更新筆記時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _delete_note(request, note_id):
    """刪除筆記"""
    try:
        from .models import NoteV2
        from .validators import APIValidator
        
        # 驗證並獲取使用者
        is_valid, user, error_response = APIValidator.validate_and_get_user(
            request, source='HEADER', required=True
        )
        if not is_valid:
            return error_response
        
        # 獲取並刪除筆記
        try:
            note = NoteV2.objects.get(id=note_id, user=user)
            note_title = note.title  # 保存標題用於日誌
            note.delete()
            
            logger.info(f"Deleted note {note_id} ({note_title}) for user: {user.line_user_id}")
            
            return APIValidator.create_success_response({
                "message": "筆記已刪除",
                "id": note_id,
                "title": note_title
            })
            
        except NoteV2.DoesNotExist:
            return APIValidator.create_error_response(
                error_type="not_found",
                message="筆記不存在",
                code="NOTE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="無效的筆記 ID 格式",
                code="INVALID_NOTE_ID",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    except ImportError as e:
        logger.error(f"Import error in delete note: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "模型導入錯誤",
            "details": str(e),
            "code": "MODEL_IMPORT_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}", exc_info=True)
        return Response({
            "error": "internal_error",
            "message": "刪除筆記時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def manage_note(request, note_id):
    """
    更新或刪除筆記
    
    PUT/PATCH /api/v2/notes/<note_id>/
    DELETE /api/v2/notes/<note_id>/
    """
    if request.method in ["PUT", "PATCH"]:
        return _update_note(request, note_id)
    elif request.method == "DELETE":
        return _delete_note(request, note_id)


@api_view(["GET", "HEAD"])
@permission_classes([AllowAny])
def get_exams(request):
    """
    獲取考試列表（暫時返回空列表）
    
    GET /api/v2/exams/?line_user_id=U123456789
    HEAD /api/v2/exams/?line_user_id=U123456789
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
        
        # 如果是 HEAD 請求，只返回狀態碼，不需要處理資料
        if request.method == "HEAD":
            return Response(status=status.HTTP_200_OK)
        
        # 暫時返回空列表，未來可以實作考試功能
        logger.info(f"Retrieved exams for user: {line_user_id}")
        
        return Response([], status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving exams: {str(e)}")
        return Response({
            "error": "internal_error",
            "message": "獲取考試時發生錯誤",
            "details": str(e),
            "code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)