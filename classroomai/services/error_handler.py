"""
錯誤處理服務
統一處理 Google API 錯誤和業務邏輯錯誤
"""
import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from googleapiclient.errors import HttpError
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class APIErrorHandler:
    """API 錯誤處理器"""
    
    # Google API 錯誤碼對應
    GOOGLE_ERROR_MAPPING = {
        400: {
            'code': 'GOOGLE_BAD_REQUEST',
            'message': 'Google API 請求格式錯誤'
        },
        401: {
            'code': 'GOOGLE_UNAUTHORIZED',
            'message': 'Google 授權失效，請重新授權'
        },
        403: {
            'code': 'GOOGLE_FORBIDDEN',
            'message': 'Google API 權限不足'
        },
        404: {
            'code': 'GOOGLE_NOT_FOUND',
            'message': '請求的 Google 資源不存在'
        },
        429: {
            'code': 'GOOGLE_RATE_LIMIT',
            'message': 'Google API 請求頻率過高，請稍後再試'
        },
        500: {
            'code': 'GOOGLE_SERVER_ERROR',
            'message': 'Google 伺服器錯誤'
        },
        503: {
            'code': 'GOOGLE_SERVICE_UNAVAILABLE',
            'message': 'Google 服務暫時無法使用'
        }
    }
    
    @staticmethod
    def handle_google_api_error(error: HttpError) -> Dict[str, Any]:
        """
        處理 Google API 錯誤
        
        Args:
            error: Google API HttpError
            
        Returns:
            Dict: 標準化的錯誤回應
        """
        error_status = error.resp.status
        error_content = error.content.decode('utf-8') if error.content else ''
        
        # 獲取對應的錯誤訊息
        error_info = APIErrorHandler.GOOGLE_ERROR_MAPPING.get(
            error_status,
            {
                'code': 'GOOGLE_UNKNOWN_ERROR',
                'message': f'Google API 未知錯誤 (HTTP {error_status})'
            }
        )
        
        # 特殊處理某些錯誤
        if error_status == 404:
            if 'course' in error_content.lower():
                error_info['message'] = '課程不存在或無權限訪問'
            elif 'coursework' in error_content.lower():
                error_info['message'] = '作業不存在或無權限訪問'
        
        elif error_status == 403:
            if 'insufficient permission' in error_content.lower():
                error_info['message'] = '權限不足，請檢查 Google Classroom 權限設定'
        
        logger.error(f"Google API Error: {error_status} - {error_content}")
        
        return {
            'error': 'google_api_error',
            'message': error_info['message'],
            'code': error_info['code'],
            'details': {
                'status_code': error_status,
                'content': error_content[:500]  # 限制錯誤內容長度
            }
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, field: str = None) -> Dict[str, Any]:
        """
        處理資料驗證錯誤
        
        Args:
            error: 驗證錯誤
            field: 錯誤欄位名稱
            
        Returns:
            Dict: 標準化的錯誤回應
        """
        error_message = str(error)
        
        # 常見驗證錯誤的友善訊息
        if 'required' in error_message.lower():
            message = f"缺少必要欄位: {field}" if field else "缺少必要欄位"
        elif 'invalid' in error_message.lower():
            message = f"欄位格式錯誤: {field}" if field else "資料格式錯誤"
        elif 'date' in error_message.lower():
            message = "日期格式錯誤，請使用 YYYY-MM-DD HH:MM:SS 格式"
        elif 'time' in error_message.lower():
            message = "時間格式錯誤，請使用 HH:MM:SS 格式"
        else:
            message = f"資料驗證失敗: {error_message}"
        
        logger.warning(f"Validation Error: {error_message}")
        
        return {
            'error': 'validation_error',
            'message': message,
            'code': 'VALIDATION_FAILED',
            'details': {
                'field': field,
                'original_error': error_message
            }
        }
    
    @staticmethod
    def handle_permission_error(error: Exception, resource_type: str = None) -> Dict[str, Any]:
        """
        處理權限錯誤
        
        Args:
            error: 權限錯誤
            resource_type: 資源類型
            
        Returns:
            Dict: 標準化的錯誤回應
        """
        error_message = str(error)
        
        if 'google classroom' in error_message.lower():
            code = 'CLASSROOM_DATA_READONLY'
            message = '無法修改 Google Classroom 同步的資料'
        elif 'permission denied' in error_message.lower():
            code = 'PERMISSION_DENIED'
            message = f"無權限操作此{resource_type or '資源'}"
        else:
            code = 'ACCESS_DENIED'
            message = error_message
        
        logger.warning(f"Permission Error: {error_message}")
        
        return {
            'error': 'permission_denied',
            'message': message,
            'code': code
        }
    
    @staticmethod
    def create_error_response(error_dict: Dict[str, Any], http_status: int = None) -> Response:
        """
        創建標準化的錯誤回應
        
        Args:
            error_dict: 錯誤資訊字典
            http_status: HTTP 狀態碼
            
        Returns:
            Response: DRF Response 物件
        """
        # 根據錯誤類型決定 HTTP 狀態碼
        if http_status is None:
            error_code = error_dict.get('code', '')
            
            if 'UNAUTHORIZED' in error_code or 'AUTH' in error_code:
                http_status = status.HTTP_401_UNAUTHORIZED
            elif 'PERMISSION' in error_code or 'FORBIDDEN' in error_code:
                http_status = status.HTTP_403_FORBIDDEN
            elif 'NOT_FOUND' in error_code:
                http_status = status.HTTP_404_NOT_FOUND
            elif 'VALIDATION' in error_code or 'BAD_REQUEST' in error_code:
                http_status = status.HTTP_400_BAD_REQUEST
            elif 'RATE_LIMIT' in error_code:
                http_status = status.HTTP_429_TOO_MANY_REQUESTS
            elif 'SERVER_ERROR' in error_code or 'SERVICE_UNAVAILABLE' in error_code:
                http_status = status.HTTP_502_BAD_GATEWAY
            else:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return Response(error_dict, status=http_status)


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重試裝飾器，用於處理暫時性錯誤
    
    Args:
        max_retries: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff: 延遲時間倍數
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    last_exception = e
                    
                    # 只對特定錯誤進行重試
                    if e.resp.status in [429, 500, 502, 503, 504]:
                        if attempt < max_retries:
                            logger.warning(f"Attempt {attempt + 1} failed with {e.resp.status}, retrying in {current_delay}s...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                            continue
                    
                    # 不可重試的錯誤直接拋出
                    raise e
                except Exception as e:
                    # 其他錯誤不重試
                    raise e
            
            # 所有重試都失敗
            raise last_exception
        
        return wrapper
    return decorator


def handle_api_errors(func: Callable) -> Callable:
    """
    API 錯誤處理裝飾器
    統一處理 API 視圖中的錯誤
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except HttpError as e:
            error_dict = APIErrorHandler.handle_google_api_error(e)
            return APIErrorHandler.create_error_response(error_dict)
        
        except ValueError as e:
            error_dict = APIErrorHandler.handle_validation_error(e)
            return APIErrorHandler.create_error_response(error_dict)
        
        except PermissionError as e:
            error_dict = APIErrorHandler.handle_permission_error(e)
            return APIErrorHandler.create_error_response(error_dict)
        
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            error_dict = {
                'error': 'internal_error',
                'message': '系統發生未預期錯誤',
                'code': 'INTERNAL_ERROR',
                'details': str(e) if logger.isEnabledFor(logging.DEBUG) else None
            }
            return APIErrorHandler.create_error_response(error_dict, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


class RateLimiter:
    """
    簡單的速率限制器
    """
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        檢查是否允許請求
        
        Args:
            key: 限制鍵（如使用者 ID）
            limit: 限制次數
            window: 時間窗口（秒）
            
        Returns:
            bool: 是否允許請求
        """
        now = timezone.now().timestamp()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # 清理過期的請求記錄
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # 檢查是否超過限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 記錄新請求
        self.requests[key].append(now)
        return True


# 全域速率限制器實例
rate_limiter = RateLimiter()


def rate_limit(limit: int = 60, window: int = 60, key_func: Callable = None):
    """
    速率限制裝飾器
    
    Args:
        limit: 限制次數
        window: 時間窗口（秒）
        key_func: 生成限制鍵的函數
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 生成限制鍵
            if key_func:
                key = key_func(request)
            else:
                # 預設使用 line_user_id
                key = request.data.get('line_user_id') or request.GET.get('line_user_id')
            
            if key and not rate_limiter.is_allowed(key, limit, window):
                return Response({
                    'error': 'rate_limit_exceeded',
                    'message': f'請求頻率過高，請在 {window} 秒後再試',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator