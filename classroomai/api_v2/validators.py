"""
統一的 API 參數驗證工具
提供一致的參數驗證和錯誤處理機制
"""

import logging
import re
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from user.models import LineProfile

logger = logging.getLogger(__name__)


class APIValidator:
    """API 參數驗證器"""
    
    # LINE User ID 格式驗證正則表達式
    # 支援官方格式 (U + 32位十六進制) 和訪客模式格式 (guest- + UUID)
    LINE_USER_ID_PATTERN = re.compile(r'^(U[a-f0-9]{32}|guest-[a-f0-9\-]{36})$')
    
    @staticmethod
    def validate_line_user_id(request, source='GET', required=True):
        """
        驗證 line_user_id 參數
        
        Args:
            request: Django request 物件
            source: 參數來源 ('GET', 'POST', 'HEADER', 'AUTO')
            required: 是否為必要參數
            
        Returns:
            tuple: (is_valid, line_user_id, error_response)
            - is_valid: 驗證是否通過
            - line_user_id: 驗證通過的 line_user_id
            - error_response: 如果驗證失敗，返回錯誤回應物件
        """
        line_user_id = None
        
        # 根據來源獲取參數
        if source == 'GET':
            line_user_id = request.GET.get('line_user_id')
        elif source == 'POST':
            if hasattr(request, 'data'):
                line_user_id = request.data.get('line_user_id')
            else:
                import json
                try:
                    data = json.loads(request.body) if request.body else {}
                    line_user_id = data.get('line_user_id')
                except json.JSONDecodeError:
                    pass
        elif source == 'HEADER':
            line_user_id = request.META.get('HTTP_X_LINE_USER_ID')
        elif source == 'AUTO':
            # 自動檢測：優先順序 HEADER > GET > POST
            line_user_id = (
                request.META.get('HTTP_X_LINE_USER_ID') or
                request.GET.get('line_user_id')
            )
            if not line_user_id and hasattr(request, 'data'):
                line_user_id = request.data.get('line_user_id')
            elif not line_user_id:
                try:
                    import json
                    data = json.loads(request.body) if request.body else {}
                    line_user_id = data.get('line_user_id')
                except json.JSONDecodeError:
                    pass
        
        # 檢查是否缺少參數
        if not line_user_id:
            if required:
                error_response = APIValidator.create_error_response(
                    error_type="missing_parameter",
                    message="缺少 line_user_id 參數",
                    code="MISSING_LINE_USER_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                return False, None, error_response
            else:
                return True, None, None
        
        # 驗證格式
        if not APIValidator.LINE_USER_ID_PATTERN.match(line_user_id):
            error_response = APIValidator.create_error_response(
                error_type="invalid_parameter",
                message="line_user_id 格式不正確，應為 U + 32位十六進制字符 或 guest- + UUID 格式",
                code="INVALID_LINE_USER_ID_FORMAT",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            return False, None, error_response
        
        return True, line_user_id, None
    
    @staticmethod
    def validate_user_exists(line_user_id):
        """
        驗證使用者是否存在，如果是訪客模式則自動創建
        
        Args:
            line_user_id: LINE 使用者 ID
            
        Returns:
            tuple: (user_exists, user, error_response)
        """
        try:
            user = LineProfile.objects.get(line_user_id=line_user_id)
            return True, user, None
        except LineProfile.DoesNotExist:
            # 如果是訪客模式，自動創建用戶
            if line_user_id.startswith('guest-'):
                try:
                    user = LineProfile.objects.create(
                        line_user_id=line_user_id,
                        role='guest',
                        name=f'訪客用戶_{line_user_id[-8:]}',  # 使用 ID 後8位作為名稱
                        extra={'is_guest': True, 'created_by_api': True}
                    )
                    logger.info(f"Created guest user: {line_user_id}")
                    return True, user, None
                except Exception as e:
                    logger.error(f"Failed to create guest user {line_user_id}: {str(e)}")
                    error_response = APIValidator.create_error_response(
                        error_type="internal_error",
                        message="創建訪客用戶失敗",
                        code="GUEST_USER_CREATION_FAILED",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    return False, None, error_response
            else:
                error_response = APIValidator.create_error_response(
                    error_type="not_found",
                    message="使用者不存在",
                    code="USER_NOT_FOUND",
                    status_code=status.HTTP_404_NOT_FOUND
                )
                return False, None, error_response
        except Exception as e:
            logger.error(f"Error validating user {line_user_id}: {str(e)}")
            error_response = APIValidator.create_error_response(
                error_type="internal_error",
                message="驗證使用者時發生錯誤",
                code="USER_VALIDATION_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return False, None, error_response
    
    @staticmethod
    def validate_and_get_user(request, source='AUTO', required=True):
        """
        驗證 line_user_id 並獲取使用者物件（組合方法）
        
        Args:
            request: Django request 物件
            source: 參數來源
            required: 是否為必要參數
            
        Returns:
            tuple: (is_valid, user, error_response)
        """
        # 驗證 line_user_id 參數
        is_valid, line_user_id, error_response = APIValidator.validate_line_user_id(
            request, source, required
        )
        
        if not is_valid:
            return False, None, error_response
        
        if not line_user_id:
            return True, None, None  # 非必要參數且未提供
        
        # 驗證使用者存在
        user_exists, user, error_response = APIValidator.validate_user_exists(line_user_id)
        
        if not user_exists:
            return False, None, error_response
        
        return True, user, None
    
    @staticmethod
    def validate_required_field(data, field_name, field_type=str, min_length=None, max_length=None):
        """
        驗證必要欄位
        
        Args:
            data: 資料字典
            field_name: 欄位名稱
            field_type: 欄位類型
            min_length: 最小長度（適用於字串）
            max_length: 最大長度（適用於字串）
            
        Returns:
            tuple: (is_valid, value, error_response)
        """
        value = data.get(field_name)
        
        # 檢查是否存在
        if value is None:
            error_response = APIValidator.create_error_response(
                error_type="missing_parameter",
                message=f"缺少 {field_name} 參數",
                code=f"MISSING_{field_name.upper()}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            return False, None, error_response
        
        # 類型轉換和驗證
        try:
            if field_type == str:
                value = str(value).strip()
                if not value:  # 空字串檢查
                    error_response = APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message=f"{field_name} 不能為空",
                        code=f"EMPTY_{field_name.upper()}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    return False, None, error_response
                
                # 長度檢查
                if min_length and len(value) < min_length:
                    error_response = APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message=f"{field_name} 長度不能少於 {min_length} 個字符",
                        code=f"TOO_SHORT_{field_name.upper()}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    return False, None, error_response
                
                if max_length and len(value) > max_length:
                    error_response = APIValidator.create_error_response(
                        error_type="invalid_parameter",
                        message=f"{field_name} 長度不能超過 {max_length} 個字符",
                        code=f"TOO_LONG_{field_name.upper()}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    return False, None, error_response
                    
            elif field_type == int:
                value = int(value)
            elif field_type == float:
                value = float(value)
            elif field_type == bool:
                if isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    value = bool(value)
                    
        except (ValueError, TypeError):
            error_response = APIValidator.create_error_response(
                error_type="invalid_parameter",
                message=f"{field_name} 類型不正確，期望 {field_type.__name__}",
                code=f"INVALID_TYPE_{field_name.upper()}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            return False, None, error_response
        
        return True, value, None
    
    @staticmethod
    def validate_datetime_field(data, field_name, required=True):
        """
        驗證日期時間欄位
        
        Args:
            data: 資料字典
            field_name: 欄位名稱
            required: 是否為必要欄位
            
        Returns:
            tuple: (is_valid, datetime_value, error_response)
        """
        from datetime import datetime
        from django.utils import timezone
        
        value = data.get(field_name)
        
        if not value:
            if required:
                error_response = APIValidator.create_error_response(
                    error_type="missing_parameter",
                    message=f"缺少 {field_name} 參數",
                    code=f"MISSING_{field_name.upper()}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                return False, None, error_response
            else:
                return True, None, None
        
        # 解析日期時間
        try:
            if isinstance(value, str):
                if value.endswith('Z'):
                    datetime_value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    datetime_value = datetime.fromisoformat(value)
                
                # 確保是 timezone-aware
                if datetime_value.tzinfo is None:
                    datetime_value = timezone.make_aware(datetime_value)
            else:
                datetime_value = value
                
            return True, datetime_value, None
            
        except (ValueError, TypeError) as e:
            error_response = APIValidator.create_error_response(
                error_type="invalid_parameter",
                message=f"{field_name} 格式不正確，請使用 ISO 格式 (YYYY-MM-DDTHH:MM:SS)",
                code=f"INVALID_{field_name.upper()}_FORMAT",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            return False, None, error_response
    
    @staticmethod
    def create_error_response(error_type, message, code, status_code, details=None):
        """
        創建統一格式的錯誤回應
        
        Args:
            error_type: 錯誤類型
            message: 使用者友好的錯誤訊息
            code: 錯誤代碼
            status_code: HTTP 狀態碼
            details: 詳細錯誤資訊（可選）
            
        Returns:
            Response: DRF Response 物件
        """
        from django.utils import timezone
        
        error_data = {
            "error": error_type,
            "message": message,
            "code": code,
            "timestamp": timezone.now().isoformat()
        }
        
        if details:
            error_data["details"] = details
        
        # 記錄錯誤日誌
        if status_code >= 500:
            logger.error(f"API Error {status_code}: {error_type} - {message}")
        else:
            logger.warning(f"API Error {status_code}: {error_type} - {message}")
        
        return Response(error_data, status=status_code)
    
    @staticmethod
    def create_success_response(data, status_code=status.HTTP_200_OK, meta=None):
        """
        創建統一格式的成功回應
        
        Args:
            data: 回應資料
            status_code: HTTP 狀態碼
            meta: 元資料（可選）
            
        Returns:
            Response: DRF Response 物件
        """
        from django.utils import timezone
        
        response_data = {
            "data": data,
            "timestamp": timezone.now().isoformat()
        }
        
        if meta:
            response_data["meta"] = meta
        
        return Response(response_data, status=status_code)


class ValidationDecorators:
    """驗證裝飾器"""
    
    @staticmethod
    def validate_line_user_id(source='AUTO', required=True):
        """
        驗證 line_user_id 的裝飾器
        
        Args:
            source: 參數來源
            required: 是否為必要參數
        """
        def decorator(view_func):
            def wrapper(request, *args, **kwargs):
                is_valid, user, error_response = APIValidator.validate_and_get_user(
                    request, source, required
                )
                
                if not is_valid:
                    return error_response
                
                # 將使用者物件添加到 kwargs 中
                kwargs['user'] = user
                kwargs['line_user_id'] = user.line_user_id if user else None
                
                return view_func(request, *args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def handle_exceptions(view_func):
        """
        統一異常處理裝飾器
        """
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Unhandled exception in {view_func.__name__}: {str(e)}", exc_info=True)
                
                return APIValidator.create_error_response(
                    error_type="internal_error",
                    message="伺服器內部錯誤",
                    code="INTERNAL_ERROR",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details=str(e) if hasattr(e, '__str__') else "Unknown error"
                )
        
        return wrapper
    
    @staticmethod
    def support_head_requests(view_func):
        """
        支援 HEAD 請求的裝飾器
        """
        def wrapper(request, *args, **kwargs):
            # 如果是 HEAD 請求，先執行參數驗證，然後返回空回應
            if request.method == "HEAD":
                # 執行原函數進行參數驗證，但不返回資料
                try:
                    response = view_func(request, *args, **kwargs)
                    # 如果是錯誤回應，直接返回
                    if response.status_code >= 400:
                        return response
                    # 否則返回空的成功回應
                    return Response(status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error in HEAD request for {view_func.__name__}: {str(e)}")
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper